#ifndef _MOTIONSEQUENCEFORBIDDENTRANSITIONS_H_
#define _MOTIONSEQUENCEFORBIDDENTRANSITIONS_H_

#include "../src/TransitionRestrictionInterface.h"
#include "online_hmm.pb.h"

class MotionSequenceForbiddenTransitions : public TransitionRestrictionInterface {
public:
    MotionSequenceForbiddenTransitions(const std::string & motionModelName,const UIntSet_t & noMotionStates,const TransitionVector_t & forbiddenMotionTransitions);
    TransitionMultiMap_t getTimeIndexedRestrictions(const MatrixMap_t & measurements) const;
    
    hello::MotionModelRestriction * toProtobuf() const;
    
    static MotionSequenceForbiddenTransitions * createFromProtobuf(const hello::MotionModelRestriction & protobuf);
private:
    std::string _motionModelName;
    UIntSet_t _noMotionStates;
    TransitionVector_t _forbiddenMotionTransitions;
    bool isMotion(const HmmDataVec_t & motion, uint32_t t) const;
};

#endif //_MOTIONSEQUENCEFORBIDDENTRANSITIONS_H_

