#include <iostream>
#include <chrono>
#include <fstream>
#include <sstream>      // stringstream
#include <vector>
#include <unordered_map>
#include <utility>





using namespace std;
using chrono::duration_cast;
using chrono::milliseconds;
using chrono::nanoseconds;
using chrono::seconds;
using chrono::system_clock;

long Lazy_duration = 1000; //write every 1000ms
long lastWrittenTime;
string buffer = "";

// class that holds statistical data for each instrumentation region with iden
class instrumentationRegion{
public:
    string iden;
    float meanTime;
    long minTime// min time of staying in the instrumentation region,
         , maxTime
         , stdTime
         , totalTime
         , count; // count of numbers of access to instrumentation regions
    bool isLastAcessAtBeginning; // bool to indicate whether last access was at the begining or end of instrumentation region
    long lastAcessTime;
    instrumentationRegion(){}
    instrumentationRegion(string iden): iden(iden){
        meanTime = 0;
        stdTime = 0;
        totalTime = 0;
        count = 0;
        minTime = 0;
        maxTime = 0;
    }

    void add(bool isBegin, long accessTime){
        //we discard cached access if we meet a beginning or if we meet and end and cached was also end
        if (isBegin || (!isBegin && !isLastAcessAtBeginning) ){
            isLastAcessAtBeginning = isBegin;
            lastAcessTime = accessTime;
            return;      
        }
        // only case left now is we are now at end and last access was at beginning
        isLastAcessAtBeginning = false;
        long visitingTime = accessTime - lastAcessTime;
        totalTime += visitingTime;
        count++;
        meanTime = (float) totalTime / count;
        minTime = !minTime || visitingTime < minTime ? visitingTime : minTime;
        maxTime = !maxTime || visitingTime > maxTime ? visitingTime : maxTime;
    }
    

    
    string str(){
        stringstream s;
         s << "region: "
           << iden
           << endl
           << "Total number of accesses: "
           << count
           << endl
           << "Total Access Time (ns): "
           << totalTime
           << endl
           << "Mean Access Time (ns): "
           << meanTime
           << endl
           << "Min Access Time (ns): "
           << minTime
           << endl
           << "Max Access Time (ns): "
           << maxTime           
           << endl << endl << endl ;
        return s.str();  
    }

};

class Instrumentations{
public:
    unordered_map<string,instrumentationRegion> regions;
    string outfile;
    Instrumentations(){}
    ~Instrumentations(){
        if (outfile.empty()) return;
        ofstream file;
        file.open (outfile);
  	    
        for (pair<string, instrumentationRegion> element : regions){
                
            file << element.second.str();
  	           
        }
        file.close()  ;
    }

    void add(bool isBegin, long accessTime, string iden, string currentOutfile){
    
        if (outfile.empty()) outfile = currentOutfile;
        // if first time adding instrumentation
        if (regions.find(iden) == regions.end()){
            instrumentationRegion r = instrumentationRegion(iden);
            regions[iden] = r;
   
        }
        
        regions[iden].add(isBegin, accessTime) ;       
        
        
        
        // write all instrumentations to outfile if more than certain till duration passed
        if (!lastWrittenTime || accessTime - lastWrittenTime  > Lazy_duration){
                  
        }
    
    }
    
    
};
    

Instrumentations instrumentations;

// write file every X amounts of ms, if file
void lazyWrite(long currentTime, string message, string outfile){

    buffer += message;
    if (!lastWrittenTime || currentTime - lastWrittenTime  > Lazy_duration){
        ofstream file;
  	    file.open (outfile, ios::app);
  	    file << buffer;
  	    file.close();
  	    buffer = "";
  	    lastWrittenTime = currentTime;
        
    }


}

void defaultInstrumentBegin(string outfile, string identifier){

    long currentTimeMilliSeconds = duration_cast<nanoseconds>(system_clock::now().time_since_epoch()).count();
    stringstream msg;
  	msg << identifier <<":Instrument Begin:"<<currentTimeMilliSeconds<<"\n" ;
    //lazyWrite(currentTimeMilliSeconds, msg.str(), outfile);
    instrumentations.add(true, currentTimeMilliSeconds, identifier, outfile);
    

}

void defaultInstrumentEnd(string outfile, string identifier){

	long currentTimeMilliSeconds = duration_cast<nanoseconds>(system_clock::now().time_since_epoch()).count();
    stringstream msg;
  	msg << identifier <<":Instrument End:"<<currentTimeMilliSeconds<<"\n" ;
    //lazyWrite(currentTimeMilliSeconds, msg.str(), outfile);
    instrumentations.add(false, currentTimeMilliSeconds, identifier, outfile);
}




