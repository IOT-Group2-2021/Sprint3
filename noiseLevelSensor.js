/* RN2483 must be plugged in slot #2 !!! */

/* See https://download.mikroe.com/documents/starter-boards/clicker-2/stm32f4/clicker2-stm32-manual-v100.pdf
for board full schematic and pins assignment */


var _RN2483;                                   // modem lora
var serialRxData="";                           //recieved data from modem
var mst= "conf_appeui";                        //machine state
var Timeout;                                   //time used for active wainting
var APPEUI ="70B3D57ED003EFED";                // appeui used at subscribtion
var APPKEY ="751CED45BED10BCA93929902E9943BFD";//appkey used to subscribe into the TTN application

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
 function strcmp(a, b)
 {   
     return (a<b?-1:(a>b?1:0));  
 }
 function processing(data){

    console.log("decoded rx :",data);
    const byteSize = (data.length)-2;// not counting whitespace
    var threshold=0;
    //TESTING THE SIZE OF RECIEVED DATA
    if(byteSize!= 8){
        console.log("to much bytes recieved :",byteSize,"bytes");
    }else{
        //extract ocpde and data
        var opcode = parseInt(data.substring(0, 4),16);//decode from hexa
        var dataRaw = parseInt(data.substring(4),16);
        console.log("the rx opcode :",opcode);
        console.log("the rx data ",dataRaw);
        
        //if the opcode is correct
      if(opcode==3325){
        threshold=parseInt(dataRaw);
        console.log("recieved threshold :",threshold);

        if(threshold>5555){//to do
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
                    console.log("Nclick configuration");
                    SPI_init();
                    DAC_init(6600);
                    sensor_conf();      
                    mst = "hold";
                    sendToRn2483("mac save");
                    console.log("Starting measurement ...");
                }
                break;
            case "send_payload":
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
        }
        serialRxData="";
    }
});


/************************ Sensor  configuration *************** */
var EN   =E7;
var CS   =E8;
var INT  =E10;
var SCK  =C10;
var MISO =C11;
var MOSI =C12;
var HIGH =1;
var LOW  =0;
var OUT =0;
var DETECTION =1;
/**
 * initilize SPI interfaces
 */
function SPI_init(){
console.log("SPI inititiazing... ");
SPI3.setup({
    sck:SCK, 
    miso:MISO, 
    mosi:MOSI, 
    baud:integer=100000, 
    mode:integer=0, // between 0 and 3
    order:string='msb' // can be 'msb' or 'lsb' 
   });
}

/**
 * initialize DAC
 * VOUT = (VReef*GDn)/2^n
 */
function DAC_init(value){
    console.log("DAC inititiazing... ");
    _regDAC=0b00110000;
    _mask=0b0000000011111111;
    _firstByte=(value>>8) | _regDAC;
    _secondByte=value& _mask;
    _firstByte &= ~ (1 << 7);

    digitalWrite(CS,LOW); //select the DAC
    SPI3.write(_firstByte);
    SPI3.write(_secondByte);
    digitalWrite(CS,HIGH);

}
/**
 * sensor configuration
 */
function sensor_conf(){
    
    set_threshold(uint16(600));
}

function set_threshold( value){
value |= 0x7000;
digitalWrite(CS,LOW); //select the DAC
SPI3.write(value);
digitalWrite(CS,HIGH);
}
function encapsulation(value){
    opc="CFC";//3324
    final=(opc)+"0"+(value);
    console.log("final :",final);
    return final;
}
setWatch(function () {

    OUT=((analogRead(A2))*3300).toFixed(1);
    console.log("analog output :",OUT);
    console.log("noise detected ");
    encoded=(OUT*10).toString(16);
    console.log("encoded value :",encoded);
    toSend=encapsulation(encoded);
    console.log("final value with opcode :",toSend);
    sendToRn2483_Timeout(toSend);

},E10,{repeat:true,edge:'falling'});

function uint16 (n) {
return n & 0xFFFF;
}

save();
