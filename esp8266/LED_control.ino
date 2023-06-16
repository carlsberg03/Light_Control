  #include <ESP8266WiFi.h>        // 本程序使用 ESP8266WiFi库
  #include <ESP8266WiFiMulti.h>   //  ESP8266WiFiMulti库
  #include <ESP8266WebServer.h>   //  ESP8266WebServer库

  #define RGB_RG_0  D1  // 红绿灯引脚号
  #define RGB_B_0   D0  // 蓝灯引脚号
  #define RGB_RG_1  D3  // 红灯引脚号
  #define RGB_B_1   D2  // 蓝灯引脚号
  #define RGB_RG_2  D5  // 红灯引脚号
  #define RGB_B_2   D4  // 蓝灯引脚号
  #define RGB_RG_3  D7  // 红灯引脚号
  #define RGB_B_3   D6  // 蓝灯引脚号

  const char* ssid     = "P40";               // 连接WiFi名
  const char* password = "12345678";          // 连接WiFi密码

  const char* host = "192.168.43.122";    // 网络服务器IP
  const int   Port = 8888;                // 端口号为8888

  IPAddress dns(192,168,0,1);           // 设置局域网DNS的IP（通常局域网DNS的IP是WiFI路由IP）
  IPAddress sta_local_ip(192,168,43,10); // 设置ESP8266-NodeMCU联网后的IP
  IPAddress AP_local_IP(192,168,4,22);  //手动设置的开启的网络的ip地址
  IPAddress gateway(192,168,4,9);       //手动设置的网关IP地址
  IPAddress subnet(255,255,255,0);      //手动设置的子网掩码

  ESP8266WiFiMulti wifiMulti;         // 建立ESP8266WiFiMulti对象,对象名称是'wifiMulti'
  WiFiClient client;                  // 建立WiFiClient对象



  uint8_t oldMACAddress[] = {0x40,0x22,0xD8,0x96,0x95,0x05};

  int i = 0;

  void setup(void)
  {
    Serial.begin(9600); // 启动串口通讯，波特率设置为9600
    
    
    pinMode(RGB_RG_0, OUTPUT);  
    pinMode(RGB_B_0, OUTPUT);

    pinMode(RGB_RG_1, OUTPUT); 
    pinMode(RGB_B_1, OUTPUT);

    pinMode(RGB_RG_2, OUTPUT);  
    pinMode(RGB_B_2, OUTPUT);

    pinMode(RGB_RG_3, OUTPUT); 
    pinMode(RGB_B_3, OUTPUT);

    digitalWrite(RGB_RG_0, HIGH);
    digitalWrite(RGB_B_0, HIGH);
    digitalWrite(RGB_RG_1, HIGH);
    digitalWrite(RGB_B_1, HIGH);
    digitalWrite(RGB_RG_2, HIGH);
    digitalWrite(RGB_B_2, HIGH);
    digitalWrite(RGB_RG_3, HIGH);
    digitalWrite(RGB_B_3, HIGH);

    
    Serial.printf("正在配置网络");
    
    //无线终端模式下配置IP，并将接口的IP配置设置为用户定义的值
    WiFi.config(sta_local_ip, gateway, subnet);
    Serial.println("开始连接");
    
    //调用 WiFi.begin()函数，开始连接接入点
    WiFi.begin(ssid, password);
    Serial.print("正在连接到");
    Serial.print(ssid);

  
    
    //这里的循环用来判断是否连接成功的。连接过程中每隔500毫秒会检查一次是否连接成功，，并打一个点表示正在连接中
    //连接成功后会给出提示，但是若60秒后还是没有连接上，则会提示超时
    while (WiFi.status() != WL_CONNECTED) {
      i++;
      delay(500);
      Serial.print(".");
      if (i > 120) { //12秒后如果还是连接不上，就判定为连接超时
        Serial.print("连接超时！请检查网络环境");
        break;
      }
    }  
    if (i < 120) 
    {
      Serial.print("\n连接成功");
      //这一部分用来输出连接网络的基本信息
      Serial.print("当前工作模式:");     // 告知用户设备当前工作模式
      Serial.println(WiFi.getMode());
      Serial.print("连接到的接入点名字:");
      Serial.println(ssid);            // 告知用户连接到的接入点WiFi名
      Serial.print("连接到的接入点密码:");
      Serial.println(password);        // 告知用户连接到的接入点WiFi密码
      Serial.print("无线终端模式成功开启");
      Serial.print("当前无线终端静态IP地址： ");// 告知用户当前无线终端的IP地址(也就是我们设置的地址)
      Serial.println(WiFi.localIP());
      Serial.print("当前无线终端网关的IP地址： ");// 告知用户当前无线终端网关的IP地址
      Serial.println(WiFi.gatewayIP());
      Serial.print("当前无线终端： ");// 告知用户当前无线终端的子网掩码地址
      Serial.println(WiFi.subnetMask());
      Serial.println("mac地址：");
      Serial.println( WiFi.macAddress());
      Serial.println("初始化完成");        
    }
  }
  void loop(){

    
    wifiClientRequest();  
    delay(10);
  }
  
  String fenge(String str,String fen,int index)
  {
    int weizhi;
    String temps[str.length()];
    int i=0;
    do
    {
        weizhi = str.indexOf(fen);
        if(weizhi != -1)
        {
          temps[i] =  str.substring(0,weizhi);
          str = str.substring(weizhi+fen.length(),str.length());
          i++;
          }
          else {
            if(str.length()>0)
            temps[i] = str;
          }
    }
      while(weizhi>=0);

      if(index>i)return "-1";
      return temps[index];
  }

  void wifiClientRequest()
  {
  
    
    String buttonState;           // 储存服务器按钮状态变量  
          
    Serial.print("Connecting to"); Serial.print(host);
  
    // 连接服务器
    if (client.connect(host, Port))
    {
      Serial.println(" Success!");
      while (client.connected() || client.available())
      { 
        String line = client.readStringUntil('\n');     //运行一次只接收一组灯光的控制数据字符数据之间用空格隔开
        Serial.println(line);  
        LED_c(line);
      }
    }
    else
    {
      Serial.println(" failed!");
    } 
  }
  void LED_c(String line)
  {
    int Val1,Val2,Val3;
    String part01 = "0";
    String part02 = "0";
    String part03 = "0";
    part01 = fenge(line," ",0);
    part02 = fenge(line," ",1);
    part03 = fenge(line," ",2);
    Val1 = part01.toInt();              //灯号
    Val2 = part02.toInt();              //色温
    Val3 = part03.toInt();              //亮度

    Val3 =256-map(Val3,0,9,0,256);     
   
    Val2 =map(Val2,0,9,Val3,256);
     Serial.println(Val2);           
     Serial.println(Val3); 
    if(Val1==1)
    { 
      analogWrite(RGB_RG_0, Val3);
     
      analogWrite(RGB_B_0, Val2);
    }
    else if(Val1==2)
    {
      analogWrite(RGB_RG_1, Val3);
      analogWrite(RGB_B_1, Val2);
    }
    else if(Val1==3)
    {
      analogWrite(RGB_RG_2, Val3);
      analogWrite(RGB_B_2, Val2);
    }
    else if(Val1==4)
    {
      analogWrite(RGB_RG_3, Val3);
      analogWrite(RGB_B_3, Val2);
    }

  }
