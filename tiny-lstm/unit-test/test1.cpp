#include "gtest/gtest.h"


class Test1 : public ::testing::Test {
protected:
    virtual void SetUp() {
        
    }
    
    virtual void TearDown() {
        
    }
    
    
};

class DISABLED_Test1 : public Test1 {};

TEST_F(Test1,TestFOO) {
    
    
}

