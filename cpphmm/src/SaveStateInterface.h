#ifndef _SAVESTATEINTERFACE_H_
#define _SAVESTATEINTERFACE_H_

class SaveStateInterface {
public:
   virtual ~SaveStateInterface() {};

   virtual void saveState(const std::string & data) = 0;

};

#endif //_SAVESTATEINTERFACE_H_
