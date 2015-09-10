# msgcenter
Pass messages between IRC and WhatsApp.

Runs on Python 2.x and 3.x (tested with 2.7.5 and 3.4.3 on Ubuntu)

#Usage
```shell
git clone https://github.com/ndob/msgcenter.git
cd msgcenter
pip install -r requirements.txt
python main.py
```
#Registering to WhatsApp
To use WhatsApp-backend you need to register to WhatsApp.  [Registering using Yowsup-cli HOW-TO] (https://github.com/tgalal/yowsup/wiki/yowsup-cli-2.0)

*NOTE*: You can't use the same account on your phone and with this program. Only one device can be logged in at any given time.

**Quickstart**

1. Request registration code as SMS.
  ```shell
  yowsup-cli registration --requestcode sms --phone 49XXXXXXXX --cc 49 --mcc 123 --mnc 456
  ```

2. Register with the code you got as a SMS.
  ```shell
  yowsup-cli registration --register 123456 --phone 49XXXXXXXX --cc 49  
  ```

3. List group chats, that you belong to.
  ```shell
  yowsup-cli demos --yowsup -l 358505555555:base64-encoded-whatsapp-password
  ```
  ```shell
  /L
  /groups list
  ```

#Configuration
Example configuration in config.json.

**Backend configuration**

Defines a backend, which is a IRC server or WhatsApp-account.

- Key: name for backend
- Value: 
  - type: "irc" or "whatsapp"
  - phone (only for WhatsApp): phone number registered to WhatsApp (see [registering](.#Registering to WhatsApp))
  - password (only for WhatsApp): password for WhatsApp account (see [registering](.#Registering to WhatsApp))
  - server (only for IRC): server address
  - port (only for IRC): server port
  - nick (only for IRC): nickname to use in IRC

**Group configuration**

Defines a group. Messages will be sent from each specified message sink to all others.

- Key: name for group
- Value: array of message sinks

**Message sink configuration**

Defines a message sink, which can be an IRC-channel or WhatsApp group chat.

- backend: name of a backend defined in backend configuration
- channel: channel name to send the messages. eg. "#channel123" for IRC or "358505555555-1000000000@g.us" for WhatsApp
