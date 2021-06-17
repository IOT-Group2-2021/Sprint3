/* RN2483 must be plugged in slot #2 !!! */

/* See https://download.mikroe.com/documents/starter-boards/clicker-2/stm32f4/clicker2-stm32-manual-v100.pdf
for board full schematic and pins assignment */


var _RN2483;                                   // modem lora
var serialRxData="";                           //recieved data from modem
var mst= "conf_appeui";                        //machine state
var Timeout;                                   //time used for active wainting
var APPEUI ="70B3D57ED003EFED";                // appeui used at subscribtion
var APPKEY ="B3A3A3B1B94F66075E244544FA9E4AE3";//appkey used to subscribe into the TTN application
var active =false;                             //sensor state
var TEMP;                                      //tempurature
var Sampling=60000;
var idSamplingInterval;
var presence="01";
/**************General system *************** */

/* RN2483 reset function - calling this function should print something
like "RN2483 1.0.4 Oct 12 2017 14:59:25" */
function resetRn2483(){
  pinMode(E13, "output");
  digitalWrite(E13, 1);
  digitalPulse(E13, 0, 200);
  
}

/* The onInit() function is called at board reset */
function onInit() {
    console.log("========== Program started ==========\r\n");
    resetRn2483();
    //IR_Configuration();
    MODEM_Configuration();
  }
/***************Modem RN2483A*********************/


function MODEM_Configuration(){
    /* Serial port initialisation (the "/25*8" is a work-around because of bad
    internal clock initialisation) */
    Serial3.setup(57600/25*8, { tx:D8, rx:D9 });
    modem =require("RN2483");
    _RN2483=new modem(Serial3,{reset:E13,debug:false}); 
} 

/* Send a string to RN2483 with the syntax "sendToRn2483("COMMAND_TO_SEND")".
The <CR><LF> characters are automatically added by the Serial3.println() function
See https://ww1.microchip.com/downloads/en/DeviceDoc/40001784B.pdf for full
command reference */
function sendToRn2483(string) {
    console.log("Command sent: "+ string);
    Serial3.println(string);
  }

/** Send a packet with a timemout*/
function sendToRn2483_Timeout(data){
        mst="send_payload";
        sendToRn2483("mac tx uncnf 3 "+data);
        holdTime();  
}

 function holdTime(){
     Timeout= setTimeout(function(){
             mst="hold";
     },10000);
 }

 
 function setSampling(value){
     Sampling=value;
    clearInterval(idSamplingInterval);
    idSamplingInterval=setInterval(readData,value);
    console.log("sampling set to "+value +" ms");
    digitalWrite(E15,1);
 }
 function strcmp(a, b)
 {   
     return (a<b?-1:(a>b?1:0));  
 }
 /*
 function processing(data){

   var decoded=parseInt(data, 16);
   console.log(parseInt(data, 16));
   if (decoded == 1){//message from #node2 
    digitalWrite(E12,1);
   }else if (decoded >= 30000 && decoded <= 60000){ // message from #bot
    setSampling(decoded);
   }else{
     console.log("recieved unkown message");
   }
 }
 */
 function processing(data){

  console.log("decoded rx :",data);
  const byteSize = (data.length)-2;// not counting whitespace
  var threshold=0;
  //TESTING THE SIZE OF RECIEVED DATA
  if(byteSize!= 6){
      console.log("to much bytes recieved :",byteSize,"bytes");
  }else{
      //extract ocpde and data
      var opcode = parseInt(data.substring(0, 4),16);//decode from hexa
      var dataRaw = parseInt(data.substring(4),16);
      console.log("the rx opcode :",opcode);
      console.log("the rx data ",dataRaw);
      
      //if the opcode is correct
    if(opcode==3304){
      threshold=(parseInt(dataRaw))/2;
      console.log("recieved threshold :",threshold);

      if(threshold>70){//to do
          digitalWrite(E15,1);
      }else{
          digitalWrite(E12,1);
      }
    }else{
        console.log("opcode not correct !");
    }
  }
}
/* This is the callback called when character appears on the serial port */
/**  State machine :
 *                (1) conf_appeui : configure the appui for the node
 *                (2) conf_appkey : configure the appkey of the application
 *                (3) join_otaa   : connect the node to the TTN server
 *                (4) start_sensor: starting the sensor 
 *                (5) send_payload: sending data 
 *                (6) hold        : this state used like a standby state    
*/
Serial3.on('data',function(data){
    serialRxData=serialRxData+data;
    if(serialRxData.indexOf("\r\n")!= -1){
        console.log(serialRxData);
        switch(mst){
            case "conf_appeui":
                if(serialRxData.indexOf("RN2483 1.0.4")!= -1){
                    mst = "conf_appkey";
                    sendToRn2483("mac set appeui "+ APPEUI);
                }
                break;
            case "conf_appkey":
                if(serialRxData.indexOf("ok")!= -1){
                    mst = "data_rate";
                    sendToRn2483("mac set appkey "+ APPKEY);
                }
                break;
            case "data_rate":
              if(serialRxData.indexOf("ok")!= -1){
                mst = "join_otaa";
                sendToRn2483("mac set dr 5");
            }
            break;
            case "join_otaa":
                if(serialRxData.indexOf("ok")!= -1){
                    mst = "start_sensor";
                    sendToRn2483("mac join otaa");
                }
                break;
            case "start_sensor":
                if(serialRxData.indexOf("accepted")!= -1){
                    console.log("IR configuration");
                    IR_Configuration();
                    //mst = "hold";
                    //save config
                    sendToRn2483("mac save");
                    console.log("Starting measurement ...");
                    active=true;
                    //edit cntl2 to continous mode
                    i2c_write_reg(0x64,0x15,0xFD);
                    idSamplingInterval= setInterval(readData,Sampling);
                   
                      //console.log("Temp = "+TEMP);, Sampling);
    
                }
                break;
            case "send_payload":
              //reset LED's
                digitalWrite(E15,0);
                digitalWrite(E12,0);

                if(serialRxData.indexOf("mac_tx_ok") != -1){
                  console.log("--sending--")
                    mst = 'hold';
                  clearTimeout(Timeout);
                }else if (serialRxData.indexOf("mac_rx")!=-1) {
                  console.log("--recieving-")
                  console.log("message rx : "+ serialRxData.split(" ")[2]);
                  processing(serialRxData.split(" ")[2]);
                  mst = 'hold';
                  clearTimeout(Timeout);
                  
                }
                  break; 
            default:
                break;
        }
        serialRxData="";
    }
});

/************************ Sensor  configuration *************** */

/**
 * Configure the sensor
 */
function IR_Configuration(){
  I2C3.setup({scl:A8,sda:C9});
  i2c_write_reg(0x64,0x16,0xFF);// cntl3 adr = 0x16 , SRST (bit 0= 1) donc FF
  i2c_write_reg(0x64,0x14,0xED);// cntl1 (5 bits) adr =0x14 ,cut-off FC temp =2.5 Hz (001), FC IR=0.45 (11) 
  i2c_write_reg(0x64,0x13,0xF8);//   inten adr = 0x13  , interrupts only IR
  set_IR_thresh(10,0);
}
/** start and stop IR sensor
 * addr :0x15 CNTL2 111111 MODE MODE
 * MODE[1:0]: Operating Mode Setting
              "00": Stand by Mode
              "01": Continuous Mode
              "10": Single Shot Mode
              "11": Prohibited
 */
setWatch(function(){
  if(active===false){
    console.log("Starting measurement ...");
    active=true;
    //edit cntl2 to continous mode
    i2c_write_reg(0x64,0x15,0xFD);
  }else {
    console.log("Stopping measurement ...");
    active=false;
    //edir cntl2 to standby mode
    i2c_write_reg(0x64,0x15,0xFC);//
  }

},E0,{repeat:true,edge:'falling',debounce:10});

function encapsulation(value){
    
  //var opCode=3324;
  //opc=opCode.toString(16);
  opc_temp="0CE7";//3303
  opc_presence="0CE6";//3302
  final=(opc_temp)+"0"+(value*10).toString(16)+opc_presence+presence;
  console.log("final :",final);
  return final;
}
/**
 * Read data from sensor every time the crossed 
 */
function readData(){
  /** start reading fron st1 register  */
  update = i2c_burst_read(0x64,0x04,7);
 // console.log("update"+update);
  /** Indicated value of Temperature Sensor (ººC) = C) = 0.001983737 Measurement data of Temperature Sensor (Decimal) + 25 */
  c=(0.0019837*_2complement(concatReg(update[5],update[4]))+25).toFixed(1);
  //TEMP = ((5/9) * (c - 32)).toFixed(2);
  /** Output current of IR Sensor (pA) = 0.4578 Measurement data of IR Sensor (Decimal) */
  Ir=0.4578*_2complement(concatReg(update[3],update[2]));
  //status=Serial3.println("mac get status");
  //status&=14;
  //if(status==0){//channel available 
  console.log("tempurature = "+ c+" °C");
  presence="00";
  enc=encapsulation(c);
  sendToRn2483_Timeout(enc);
  //}
  
}

setWatch( function (){
    /** start reading fron st1 register  */
    update = i2c_burst_read(0x64,0x04,7);
    // console.log("update"+update);
     /** Indicated value of Temperature Sensor (ººC) = C) = 0.001983737 Measurement data of Temperature Sensor (Decimal) + 25 */
     c=(0.0019837*_2complement(concatReg(update[5],update[4]))+25).toFixed(1);
     //TEMP = ((5/9) * (c - 32)).toFixed(2);
     /** Output current of IR Sensor (pA) = 0.4578 Measurement data of IR Sensor (Decimal) */
     Ir=0.4578*_2complement(concatReg(update[3],update[2]));
     //status=Serial3.println("mac get status");
     //status&=14;
     //if(status==0){//channel available 
     console.log("Intrusion detection , tempurature = "+ c+" °C");
     presence="01";
     enc=encapsulation(c);
     sendToRn2483_Timeout(enc);
     
},E10,{repeat:true,edge:'falling'});

/**
 * Conactinate two register of 8 bits into 16 bits value
 * @param {*} regA upper 8 bits
 * @param {*} regB lower 8 bits
 * @returns 16 bits value 
 */

function concatReg(regA,regB){
  return (((regA & 0xff) << 8) | (regB& 0xff));
}
/**
 * Calculate two complement of 16 bits value
 * @param {*} value 16 bit value
 * @returns  tow complement 
 */
function _2complement(value){
  if(value >= 32767){
   return value- 32768;
  }else{
      return value;
  }
}

/**
 * Encode a string to hex value
 * @returns Hex value
 */
String.prototype.hexEncode = function(){
  var hex, i;

  var result = "";
  for (i=0; i<this.length; i++) {
      hex = this.charCodeAt(i).toString(16);
      result += (hex).slice(-4);
  }

  return result;
}


/** utils function src Benoit  */

/* General function writing a specific register through I2C */
function i2c_write_reg(address, register, value) {
I2C3.writeTo(address, register, value);
}

/* General function reading several registers in a row through I2C */
function i2c_burst_read(address, register, burst) {
I2C3.writeTo(address, register);
return I2C3.readFrom(address, burst);
}
/** dedicated function configuring the AK9752 IR thresholds */
function set_IR_thresh(high_thresh, low_thresh){

  if(high_thresh >32767 || high_thresh < -32767 || low_thresh >32767 || low_thresh < -32767){
      return NaN;
  }
  var high_thresh_L=0, high_thresh_H=0,low_thresh_L=0,low_thresh_H=0;

  if(high_thresh >= 0){
      high_thresh_L = high_thresh % 256;
      high_thresh_H =(high_thresh - high_thresh_L) / 256;
  }else {
      high_thresh_L =(high_thresh + 32768)% 256;
      high_thresh_H=(high_thresh  + 32768 -high_thresh_L)/256 +128;
  }
  if(low_thresh>=0){
      low_thresh_L=low_thresh% 256;
      low_thresh_H =(low_thresh- low_thresh_L)/256;       
  } else {
      low_thresh_L = (low_thresh + 32768)% 256;
      low_thresh_H = (low_thresh + 32768 - low_thresh_L)/256 + 128;
  }
  i2c_write_reg(0x64,0x0B,[high_thresh_L,high_thresh_H,low_thresh_L,low_thresh_H]);
}

save();
