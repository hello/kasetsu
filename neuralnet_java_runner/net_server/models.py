from boto.s3.connection import S3Connection
import os
from keras.models import model_from_json
import logging
import string
import random

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def get_models_from_s3(bucket):
    configs = {}
    values = {}

    conn = S3Connection()
    bucket = conn.get_bucket(bucket)
    for key in bucket.list():
        name = key.name.encode('utf-8')
        model_name = name.split('.')[0]
        if 'json' in name:
            logging.info('action=download bucket=%s key=%s' % (bucket,name))
            value = bucket.get_key(name)
            model_config = value.get_contents_as_string()
            try:
                values_name = name.replace('json','h5')
                logging.info('action=download bucket=%s key=%s' % (bucket,values_name))
                model_values = bucket.get_key(values_name)
                values[model_name] = values_name,model_values
                configs[model_name] = model_config
            except Exception,e:
                logging.error('bucket=%s key=%s error=\"%s\"' % (bucket,name,e))

    models = {}
    for key in configs:
        logging.info('action=compiling model=%s' % key)
        models[key] = model_from_json(configs[key])            

    for key in configs:
        vname,data = values[key]
        filename = vname + '.' + id_generator(16)
        with open(filename,'w') as f:
            #hacky as fuck
            f.write(data.get_contents_as_string())

        models[key].load_weights(filename)
        os.remove(filename)

    return models

def get_models_from_local(path):
    files = os.listdir(path)
    config_files = [f for f in files if "json" in f]
    models = {}


    for fname in config_files:
        with open(fname,'r') as f:
            config = f.read()
            key = fname.split(".")[0]
            logging.info('action=compiling model=%s' % key)
            models[key] = model_from_json(config)
            models[key].load_weights(key + '.h5')

    return models

        
if __name__ == '__main__':
    get_models_from_s3('hello-neuralnet-models')
