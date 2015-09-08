#include "MotionSequenceForbiddenTransitions.h"
#include "DataFile.h"

MotionSequenceForbiddenTransitions::MotionSequenceForbiddenTransitions(const std::string & motionModelName, const UIntSet_t &  noMotionStates, const TransitionVector_t & forbiddenMotionTransitions) {
    _motionModelName = motionModelName;
    _noMotionStates = noMotionStates;
    _forbiddenMotionTransitions = forbiddenMotionTransitions;
}

TransitionMultiMap_t MotionSequenceForbiddenTransitions::getTimeIndexedRestrictions(const MatrixMap_t & measurements) const {
    TransitionMultiMap_t forbiddenTransitions;
    
    auto it = measurements.find(_motionModelName);
    
    if (it == measurements.end()) {
        return forbiddenTransitions;
    }
    
    const HmmDataVec_t & vec = (*it).second[0];
    
    
    for (int t = 0; t < vec.size() - 1; t++) {
        //need two consecutive motion events to have a wake
        //I hypothessize that it improve things because it gets rid of bed-making events
        if (  !( isMotion(vec, t)
                && isMotion(vec, t+1)
        ))  {
            
            for (auto itTransition = _forbiddenMotionTransitions.begin(); itTransition != _forbiddenMotionTransitions.end(); itTransition++) {
                                
                forbiddenTransitions.insert(std::make_pair(t, StateIdxPair((*itTransition).from,(*itTransition).to)));

            }
            
        }
        
    }
    
    return forbiddenTransitions;
    
    
}

bool MotionSequenceForbiddenTransitions::isMotion(const HmmDataVec_t & motion, uint32_t t) const {
    const uint32_t meas = (uint32_t) motion[t];
    
    auto it = _noMotionStates.find(meas);
    
    return it == _noMotionStates.end();
}

hello::MotionModelRestriction * MotionSequenceForbiddenTransitions::toProtobuf() const {
    hello::MotionModelRestriction * protobuf = new hello::MotionModelRestriction();
    
    protobuf->set_motion_model_id(_motionModelName.c_str());
    
    for (auto it = _forbiddenMotionTransitions.begin(); it != _forbiddenMotionTransitions.end(); it++) {
        hello::Transition * transition = protobuf->add_forbiddeden_motion_transitions();
        transition->set_from((*it).from);
        transition->set_to((*it).to);
    }
    
    for (auto it = _noMotionStates.begin(); it != _noMotionStates.end(); it++) {
        protobuf->add_non_motion_states(*it);
    }
    
    return protobuf;
}

MotionSequenceForbiddenTransitions * MotionSequenceForbiddenTransitions::createFromProtobuf(const hello::MotionModelRestriction & protobuf) {
    
    
    UIntSet_t nonMotionStates;
    for (int i = 0; i < protobuf.non_motion_states_size(); i++) {
        nonMotionStates.insert(protobuf.non_motion_states(i));
    }
    
    TransitionVector_t transitions;
    for (int i = 0; i < protobuf.forbiddeden_motion_transitions_size(); i++) {
        const hello::Transition & transition = protobuf.forbiddeden_motion_transitions(i);
        
        StateIdxPair pair(transition.from(),transition.to());
        transitions.push_back(pair);
    }
    
    return new MotionSequenceForbiddenTransitions(protobuf.motion_model_id(),nonMotionStates,transitions);

}



