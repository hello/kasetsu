#include "InitialModelGenerator.h"
#include "CompositeModel.h"
#include "AllModels.h"
#include "MatrixHelpers.h"

#define MIN_INIT_STATE_FRACTION (0.01)

static const HmmFloat_t low_light = 0.1;
static const HmmFloat_t med_light = 3.0;
static const HmmFloat_t high_light = 6.0;
static const HmmFloat_t light_stddev = 1.0;

static const HmmFloat_t low_motion = 0.1;
static const HmmFloat_t med_motion = 8.0;
static const HmmFloat_t high_motion = 20.0;
static const HmmFloat_t low_motion_stddev = 5.0;
static const HmmFloat_t med_motion_stddev = 5.0;
static const HmmFloat_t high_motion_stddev = 5.0;

static const HmmFloat_t low_sound = 1.0;
static const HmmFloat_t med_sound = 3.0;
static const HmmFloat_t high_sound = 6.0;
static const HmmFloat_t sound_stddev = 1.0;

static const HmmFloat_t low_disturbance = 0.20;
static const HmmFloat_t high_disturbance = 0.80;

//static const HmmFloat_t minus_ratio = -1.0;
//static const HmmFloat_t plus_ratio = 1.0;
//static const HmmFloat_t even_ratio = 0.0;
//static const HmmFloat_t energy_std_dev = 1.0;

#define NUM_LIGHT_MODELS (3)
#define NUM_MOTION_MODELS (3)
#define NUM_SOUND_MODELS (3)
#define NUM_DISTURBANCE_MODELS (2)
#define NUM_ENERGY_RATIO_MODELS (3)

static const HmmFloat_t light_params[2][NUM_LIGHT_MODELS] = {
    {low_light,med_light,high_light},
    {light_stddev,light_stddev,light_stddev}};

static const HmmFloat_t sound_params[2][NUM_SOUND_MODELS] = {
    {low_sound,med_sound,high_sound},
    {sound_stddev,sound_stddev,sound_stddev}};


static const HmmFloat_t motion_gamma_params[2][NUM_MOTION_MODELS] = {
    {low_motion,med_motion,high_motion},
    {low_motion_stddev,med_motion_stddev,high_motion_stddev}};

static const HmmFloat_t disturbance_params[NUM_DISTURBANCE_MODELS] = {low_disturbance,high_disturbance};

//static const HmmFloat_t energy_ratio_params[NUM_ENERGY_RATIO_MODELS] = {minus_ratio,even_ratio,plus_ratio};


#define LIGHT_OBSNUM (0)
#define MOTION_OBSNUM (1)
#define DISTURBANCE_OBSNUM (2)
#define NAT_LIGHT_OBSNUM (3)
#define SOUND_OBSNUM (4)
#define PARTNER_MOTION_OBSNUM (5)


#define LIGHT_WEIGHT (1.0)
#define MOTION_WEIGHT (1.0)
#define DISTURBANCE_WEIGHT (1.0)
#define SOUND_WEIGHT (1.0)
#define NAT_LIGHT_WEIGHT (1.0)

static ModelVec_t getPartnerDiffModel() {
    ModelVec_t models;

    OneDimensionalGaussianModel gaussian1(0,0.0,10.0,1.0);
    OneDimensionalGaussianModel gaussian2(0,20.0,10.0,1.0);
    OneDimensionalGaussianModel gaussian3(0,-20.0,10.0,1.0);
    
    CompositeModel model1;
    CompositeModel model2;
    CompositeModel model3;
    
    model1.addModel(HmmPdfInterfaceSharedPtr_t(gaussian1.clone(false)));
    model2.addModel(HmmPdfInterfaceSharedPtr_t(gaussian2.clone(false)));
    model3.addModel(HmmPdfInterfaceSharedPtr_t(gaussian3.clone(false)));
    
    models.push_back(model1.clone(false));
    models.push_back(model2.clone(false));
    models.push_back(model3.clone(false));


    return models;
}

static HmmDataMatrix_t getCovarianceMatirx(HmmFloat_t std1, HmmFloat_t std2, HmmFloat_t correlation) {
    HmmDataMatrix_t mat = getZeroedMatrix(2, 2);
    
    mat[0][0] = std1*std1;
    mat[1][0] = std1*std2 * correlation;
    mat[0][1] = mat[1][0];
    mat[1][1] = std2*std2;
    
    return mat;
}

static ModelVec_t getPartnerCorrelatedModel() {
    const HmmFloat_t minstddev = 1.0;
    UIntVec_t obsnums;
    obsnums << 1,5;

    HmmDataVec_t mean1;
    mean1 << 0.0,0.0;

    HmmDataVec_t mean2;
    mean2 << 4.0,0.0;

    HmmDataVec_t mean3;
    mean3 << 0.0,4.0;
    
    HmmDataVec_t mean4;
    mean4 << 4.0,4.0;
    
    ModelVec_t models;
    
    models.push_back(MultivariateGaussian(obsnums, mean1, getCovarianceMatirx(2.0,2.0,0.1),minstddev, 1.0).clone(false));
    models.push_back(MultivariateGaussian(obsnums, mean2, getCovarianceMatirx(2.0,2.0,0.1),minstddev, 1.0).clone(false));
    models.push_back(MultivariateGaussian(obsnums, mean3, getCovarianceMatirx(2.0,2.0,0.1),minstddev, 1.0).clone(false));
    models.push_back(MultivariateGaussian(obsnums, mean4, getCovarianceMatirx(2.0,2.0,0.7),minstddev, 1.0).clone(false));

    return models;
}

static ModelVec_t getSinglePersonMotionInitialModel() {
    ModelVec_t models;
    
    //enumerate all possible models
    
    for (int iMotion = 0; iMotion < NUM_MOTION_MODELS; iMotion++) {
        
        //  OneDimensionalGaussianModel motion(MOTION_OBSNUM,motion_gamma_params[0][iMotion],motion_gamma_params[1][iMotion],MOTION_WEIGHT);
        // GammaModel motion(MOTION_OBSNUM,motion_gamma_params[0][iMotion],motion_gamma_params[1][iMotion],MOTION_WEIGHT);
        
        PoissonModel motion(MOTION_OBSNUM,motion_gamma_params[0][iMotion],MOTION_WEIGHT);
        
        
        CompositeModel model;
        model.addModel(motion.clone(false));
        
        models.push_back(model.clone(false));
        
    }

    
    return models;
}

static ModelVec_t getSinglePersonDisturbanceInitialModel() {
    ModelVec_t models;
    
    //enumerate all possible models
    
    for (int iDisturbance = 0; iDisturbance < NUM_DISTURBANCE_MODELS; iDisturbance++) {
        
        
        HmmDataVec_t disturbanceProbs;
        disturbanceProbs.resize(2);
        disturbanceProbs[0] = 1.0 - disturbance_params[iDisturbance];
        disturbanceProbs[1] = disturbance_params[iDisturbance];
        
        AlphabetModel disturbance(DISTURBANCE_OBSNUM,disturbanceProbs,true,DISTURBANCE_WEIGHT);

        
        CompositeModel model;
        model.addModel(disturbance.clone(false));
        
        models.push_back(model.clone(false));
        
        
    }
    
    return models;
}

static ModelVec_t getSinglePersonLightInitialModel() {
    ModelVec_t models;
    
    //enumerate all possible models
    for (int iNatLight = 0; iNatLight < NUM_DISTURBANCE_MODELS; iNatLight++) {
        
        for (int iLight = 0; iLight < NUM_LIGHT_MODELS; iLight++) {
            
            GammaModel light(LIGHT_OBSNUM,light_params[0][iLight],light_params[1][iLight],LIGHT_WEIGHT);
            
            HmmDataVec_t natLightProbs;
            natLightProbs.resize(2);
            natLightProbs[0] = 1.0 - disturbance_params[iNatLight];
            natLightProbs[1] = disturbance_params[iNatLight];

            AlphabetModel natLight(NAT_LIGHT_OBSNUM,natLightProbs,true,NAT_LIGHT_WEIGHT);

            
            CompositeModel model;
            model.addModel(light.clone(false));
            model.addModel(natLight.clone(false));

            models.push_back(model.clone(false));
            
        }
    }
    
    return models;
}

static ModelVec_t getSinglePersonSoundInitialModel() {
    ModelVec_t models;
    
    //enumerate all possible models
    for (int iSoundCount = 0; iSoundCount < NUM_SOUND_MODELS; iSoundCount++) {
        GammaModel sound(SOUND_OBSNUM,sound_params[0][iSoundCount],sound_params[1][iSoundCount],SOUND_WEIGHT);
        
        CompositeModel model;
        model.addModel(sound.clone(false));
        
        models.push_back(model.clone(false));
    }
    
    return models;
}

static ModelVec_t getSinglePersonInitialModel() {
    ModelVec_t models;
    
    //enumerate all possible models
    for (int iLight = 0; iLight < NUM_LIGHT_MODELS; iLight++) {
        for (int iMotion = 0; iMotion < NUM_MOTION_MODELS; iMotion++) {
            for (int iSound = 0; iSound < NUM_SOUND_MODELS; iSound++) {
                for (int iNatLight = 0; iNatLight < NUM_DISTURBANCE_MODELS; iNatLight++) {
                    for (int iDisturbance = 0; iDisturbance < NUM_DISTURBANCE_MODELS; iDisturbance++) {
                        
                        //GammaModel light(LIGHT_OBSNUM,light_params[0][iLight],light_params[1][iLight],LIGHT_WEIGHT);
                        ChiSquareModel light(LIGHT_OBSNUM,light_params[0][iLight],LIGHT_WEIGHT);

                        PoissonModel motion(MOTION_OBSNUM,motion_gamma_params[0][iMotion],MOTION_WEIGHT);
                        
                        HmmDataVec_t disturbanceProbs;
                        disturbanceProbs.resize(2);
                        disturbanceProbs[0] = 1.0 - disturbance_params[iDisturbance];
                        disturbanceProbs[1] = disturbance_params[iDisturbance];
                        
                        HmmDataVec_t natLightProbs;
                        natLightProbs.resize(2);
                        natLightProbs[0] = 1.0 - disturbance_params[iNatLight];
                        natLightProbs[1] = disturbance_params[iNatLight];
                        
                        AlphabetModel disturbance(DISTURBANCE_OBSNUM,disturbanceProbs,true,DISTURBANCE_WEIGHT);
                        
                        AlphabetModel natLight(NAT_LIGHT_OBSNUM,natLightProbs,true,NAT_LIGHT_WEIGHT);

                        //GammaModel sound(SOUND_OBSNUM,sound_params[0][iSound],sound_params[1][iSound],SOUND_WEIGHT);
                        ChiSquareModel sound(SOUND_OBSNUM,sound_params[0][iSound],SOUND_WEIGHT);

                        CompositeModel model;
                        model.addModel(light.clone(false));
                        model.addModel(motion.clone(false));
                        model.addModel(disturbance.clone(false));
                        model.addModel(sound.clone(false));
                        //model.addModel(natLight.clone(false));
        
                        models.push_back(model.clone(false));
                    }
                }
            }
        }
    }

    return models;
}

/*
static ModelVec_t getPartneredInitialModel() {
    ModelVec_t models;
    
    //enumerate all possible models
    for (int iLight = 0; iLight < NUM_LIGHT_MODELS; iLight++) {
        for (int iMotion = 0; iMotion < NUM_MOTION_MODELS; iMotion++) {
            for (int iSound = 0; iSound < NUM_SOUND_MODELS; iSound++) {
                for (int iDisturbance = 0; iDisturbance < NUM_DISTURBANCE_MODELS; iDisturbance++) {
                    for (int iNatLight = 0; iNatLight < NUM_DISTURBANCE_MODELS; iNatLight++) {
                        for (int iPartnerMotion = 0; iPartnerMotion < NUM_MOTION_MODELS; iPartnerMotion++) {
                            for (int iPartnerDisturbance = 0; iPartnerDisturbance < NUM_DISTURBANCE_MODELS; iPartnerDisturbance++) {
                                for (int iEnergyRatio = 0; iEnergyRatio < NUM_ENERGY_RATIO_MODELS; iEnergyRatio++) {
                                    
                                    GammaModel light(LIGHT_OBSNUM,light_params[0][iLight],light_params[1][iLight],LIGHT_WEIGHT);
                                    
                                    //GammaModel motion(MOTION_OBSNUM,motion_gamma_params[0][iMotion],
                                    //                  motion_gamma_params[1][iMotion],MOTION_WEIGHT);
                                    PoissonModel motion(MOTION_OBSNUM,motion_gamma_params[0][iMotion],MOTION_WEIGHT);

                                    
                                    HmmDataVec_t alphabetprobs;
                                    alphabetprobs.resize(2);
                                    alphabetprobs[0] = 1.0 - disturbance_params[iDisturbance];
                                    alphabetprobs[1] = disturbance_params[iDisturbance];
                                    
                                    AlphabetModel disturbance(DISTURBANCE_OBSNUM,alphabetprobs,true,DISTURBANCE_WEIGHT);
                                    
                                    GammaModel sound(SOUND_OBSNUM,sound_params[0][iSound],sound_params[1][iSound],SOUND_WEIGHT);
                                    
                                    HmmDataVec_t natLightProbs;
                                    natLightProbs.resize(2);
                                    natLightProbs[0] = 1.0 - disturbance_params[iNatLight];
                                    natLightProbs[1] = disturbance_params[iNatLight];
                                    
                                    
                                    AlphabetModel natLight(NAT_LIGHT_OBSNUM,natLightProbs,true,NAT_LIGHT_WEIGHT);
                                    
                                    
                                    
                                    GammaModel partnermotion(PARTNER_MOTION_OBSNUM,motion_gamma_params[0][iMotion],
                                                      motion_gamma_params[1][iMotion],MOTION_WEIGHT);
                                   
                                    
                                    HmmDataVec_t partneralphabetprobs;
                                    partneralphabetprobs.resize(2);
                                    partneralphabetprobs[0] = 1.0 - disturbance_params[iPartnerDisturbance];
                                    partneralphabetprobs[1] = disturbance_params[iPartnerDisturbance];
                                    
                                    AlphabetModel partnerdisturbance(PARTNER_DISTURBANCE_OBSNUM,partneralphabetprobs,true,DISTURBANCE_WEIGHT);
                                    
                                    OneDimensionalGaussianModel energyRatio(ENERGY_RATIO_OBSNUM,energy_ratio_params[iEnergyRatio],energy_std_dev,ENERGY_RATIO_WEIGHT);
                                    
                                    CompositeModel model;
                                    
                                    model.addModel(light.clone(false));
                                    model.addModel(motion.clone(false));
                                    model.addModel(disturbance.clone(false));
                                    model.addModel(sound.clone(false));
                                    model.addModel(natLight.clone(false));
                                    model.addModel(partnermotion.clone(false));
                                    model.addModel(partnerdisturbance.clone(false));
                                    model.addModel(energyRatio.clone(false));

                                    
                                    models.push_back(model.clone(false));
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    return models;


}
 */

InitialModel_t InitialModelGenerator::getInitialModelFromData(const HmmDataMatrix_t & meas, EInitModel_t model) {
    (void)getSinglePersonInitialModel; //so we don't get a warning
    HmmDataMatrix_t evals;
    
    ModelVec_t models;
    
    switch (model ) {
        case all:
        {
            models = getSinglePersonInitialModel();
            break;
        }
            
            
        case motion:
        {
            models = getSinglePersonMotionInitialModel();
            break;
        }
            
        case light:
        {
            models = getSinglePersonLightInitialModel();
            break;
        }
            
        case sound:
        {
            models = getSinglePersonSoundInitialModel();
            break;
        }
            
        case disturbance:
        {
            models = getSinglePersonDisturbanceInitialModel();
            break;
        }
        
        case partnerdiff:
        {
            models = getPartnerDiffModel();
            break;
        }
            
        case partnercorr:
        {
            models = getPartnerCorrelatedModel();
            break;
        }
            
        default:
        {
            std::cout << "NO INITIAL MODEL FOUND" << std::endl;
            break;
        }
    }
    
    
    //now evaluate the likelihood of each model
    for (ModelVec_t::const_iterator it = models.begin(); it != models.end(); it++) {
        const HmmPdfInterfaceSharedPtr_t & model = *it;
        
        evals.push_back(model->getLogOfPdf(meas));
    }
    
    
    HmmDataMatrix_t countmat = getZeroedMatrix(models.size(), models.size());
    
    //get path
    const uint32_t T = evals[0].size();
    UIntVec_t path;
    path.reserve(T);
    
    //for each time index, find best performing composite model
    for (int t = 0; t < T; t++) {
        int max = -INFINITY;
        int imax = 0;
        for (int j = 0; j < evals.size(); j++) {
            if (evals[j][t] > max) {
                max = evals[j][t];
                imax = j;
            }
        }
        
        //save the index of the max at this time index
        path.push_back(imax);
    }
    
    //count the transitions of the path
    //we will use this to compute the transition matrix later
    for (int t = 1; t < T; t++) {
        countmat[path[t-1]][path[t]] += 1.0;
    }
    
    //count the rows (i.e. number of times the path was at each model)
    UIntVec_t rowcounts;
    rowcounts.reserve(countmat.size());
    
    for (int j = 0; j < countmat.size(); j++) {
        HmmFloat_t sum = 0.0;
        for (int i = 0; i < countmat.size(); i++) {
            sum += countmat[j][i];
        }
        
        rowcounts.push_back(sum);
        
    }
    
    
    //keep only models that had the path for a significant amount of time
    uint32_t threshold = (HmmFloat_t)T * MIN_INIT_STATE_FRACTION;
    UIntVec_t accepted;
    UIntSet_t acceptedSet;
    
    while (accepted.size() < 2) {
    
        for (int i = 0; i < countmat.size(); i++) {
            //if not already found and above threshold
            if (rowcounts[i] > threshold && acceptedSet.find(i) == acceptedSet.end()) {
                accepted.push_back(i);
                acceptedSet.insert(i);
            }
        }
        
        threshold /= 2;
        
        if (threshold == 0) {
            break;
        }
    }
    
    HmmDataMatrix_t A = getZeroedMatrix(accepted.size(),accepted.size());

    //create new count matrix with the accepted models
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
    
    printMat("A", A);
    
    //return state transition matrix and accepted composite models
    InitialModel_t initmodel;
    initmodel.A = A;
    
    for (int i = 0; i < accepted.size(); i++) {
        const HmmPdfInterfaceSharedPtr_t p = models[accepted[i]];
        std::cout << p->serializeToJson() << std::endl;
        initmodel.models.push_back(p);
    }
    
    
    return initmodel;
}
