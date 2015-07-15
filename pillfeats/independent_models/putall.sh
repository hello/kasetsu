#!/bin/bash

../put_bayes.py -f $1 --db hmm_bayesnet_models -u '-1'
../put_bayes.py -f $1 --db hmm_bayesnet_models -u '-2'
../put_bayes.py -f $1 --db hmm_bayesnet_models -u '-3'
../put_bayes.py -f $1 --db hmm_bayesnet_models -u '-4'
../put_bayes.py -f $1 --db hmm_bayesnet_models -u '-5'

