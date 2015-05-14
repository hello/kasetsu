#include "InitialModelGenerator.h"
#include "CompositeModel.h"
#include "AllModels.h"
#include "MatrixHelpers.h"

static const HmmFloat_t low_light = 1.0;
static const HmmFloat_t med_light = 3.0;
static const HmmFloat_t high_light = 6.0;
static const HmmFloat_t light_stddev = 1.0;

static const HmmFloat_t low_motion = 0.1;
static const HmmFloat_t med_motion = 1.0;
static const HmmFloat_t high_motion = 4.0;

static const HmmFloat_t low_sound = 1.0;
static const HmmFloat_t med_sound = 3.0;
static const HmmFloat_t high_sound = 6.0;
static const HmmFloat_t sound_stddev = 1.0;

static const HmmFloat_t low_disturbance = 0.05;
static const HmmFloat_t med_disturbance = 0.5;
static const HmmFloat_t high_disturbance = 0.95;

#define NUM_LIGHT_MODELS (3)
#define NUM_MOTION_MODELS (3)
#define NUM_SOUND_MODELS (3)
#define NUM_DISTURBANCE_MODELS (3)

static const HmmFloat_t light_params[2][NUM_LIGHT_MODELS] = {
    {low_light,med_light,high_light},
    {light_stddev,light_stddev,light_stddev}};

static const HmmFloat_t sound_params[2][NUM_SOUND_MODELS] = {
    {low_sound,med_sound,high_sound},
    {sound_stddev,sound_stddev,sound_stddev}};

static const HmmFloat_t motion_params[NUM_MOTION_MODELS] = {low_motion,med_motion,high_motion};

static const HmmFloat_t disturbance_params[NUM_DISTURBANCE_MODELS] = {low_disturbance,med_disturbance,high_disturbance};

#define LIGHT_OBSNUM (0)
#define MOTION_OBSNUM (1)
#define DISTURBANCE_OBSNUM (2)
#define SOUND_OBSNUM (3)



InitialModel_t InitialModelGenerator::getInitialModelFromData(const HmmDataMatrix_t & meas) {
    ModelVec_t models;
    //enumerate all possible models
    for (int iLight = 0; iLight < NUM_LIGHT_MODELS; iLight++) {
        for (int iMotion = 0; iMotion < NUM_MOTION_MODELS; iMotion++) {
            for (int iSound = 0; iSound < NUM_SOUND_MODELS; iSound++) {
                for (int iDisturbance = 0; iDisturbance < NUM_DISTURBANCE_MODELS; iDisturbance++) {
                    
                    GammaModel light(LIGHT_OBSNUM,light_params[0][iLight],light_params[1][iLight]);
                    PoissonModel motion(MOTION_OBSNUM,motion_params[iMotion]);
                    
                    HmmDataVec_t alphabetprobs;
                    alphabetprobs.resize(2);
                    alphabetprobs[0] = 1.0 - disturbance_params[iDisturbance];
                    alphabetprobs[1] = disturbance_params[iDisturbance];

                    AlphabetModel disturbance(DISTURBANCE_OBSNUM,alphabetprobs,true);
                    
                    GammaModel sound(SOUND_OBSNUM,sound_params[0][iSound],sound_params[1][iSound]);
                    
                    CompositeModel model;
                    model.addModel(light.clone(false));
                    model.addModel(motion.clone(false));
                    model.addModel(disturbance.clone(false));
                    model.addModel(sound.clone(false));
                    
                    
                    models.push_back(model.clone(false));
                }
            }
        }
    }
    
    HmmDataMatrix_t evals;
    
    //now evaluate the likelihood of each model
    for (ModelVec_t::const_iterator it = models.begin(); it != models.end(); it++) {
        const HmmPdfInterfaceSharedPtr_t & model = *it;
        
        evals.push_back(model->getLogOfPdf(meas));
    }
    
    //now count the transitions
    
    HmmDataMatrix_t countmat = getZeroedMatrix(models.size(), models.size());
    
    //get path
    const uint32_t T = evals[0].size();
    UIntVec_t path;
    path.reserve(T);
    for (int t = 0; t < T; t++) {
        int max = -INFINITY;
        int imax = 0;
        for (int j = 0; j < evals.size(); j++) {
            if (evals[j][t] > max) {
                max = evals[j][t];
                imax = j;
            }
        }
        
        path.push_back(imax);
    }
    
    for (int t = 1; t < T; t++) {
        countmat[path[t-1]][path[t]] += 1.0;
    }
    
    UIntVec_t rowcounts;
    rowcounts.reserve(countmat.size());
    
    for (int j = 0; j < countmat.size(); j++) {
        HmmFloat_t sum = 0.0;
        for (int i = 0; i < countmat.size(); i++) {
            sum += countmat[j][i];
        }
        
        rowcounts.push_back(sum);
        
    }
    
    const uint32_t threshold = (HmmFloat_t)T * 0.05;
    UIntVec_t accepted;
    
    //select significant states
    for (int i = 0; i < countmat.size(); i++) {
        if (rowcounts[i] > threshold) {
            accepted.push_back(i);
        }
    }
    
    HmmDataMatrix_t A = getZeroedMatrix(accepted.size(),accepted.size());

    //create new count matrix
    for (int j = 0; j < A.size(); j++) {
        for (int i = 0; i < A.size(); i++) {
            A[j][i] = countmat[accepted[j]][accepted[i]];
        }
        HmmFloat_t sum = 0.0;
        for (int i = 0; i < A.size(); i++) {
            sum += A[j][i];
        }
        
        if (sum < EPSILON) {
            continue;
        }
        
        for (int i = 0; i < A.size(); i++) {
            A[j][i] /= sum;
            
            if (A[j][i] < 1e-1) {
                A[j][i] = 1e-1;
            }
        }
    }
    
    InitialModel_t initmodel;
    initmodel.A = A;
    
    for (int i = 0; i < accepted.size(); i++) {
        initmodel.models.push_back(models[accepted[i]]);
    }
    
    
    return initmodel;
}
