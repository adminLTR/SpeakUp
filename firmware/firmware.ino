#include <esp_now.h>
#include <WiFi.h>

#include "Finger.h"

#define NUM_FINGERS 5
#define RIGHT_HAND // left sends data to right, right processes all data

// IMPORTANT TO CHANGE THIS ADDRESS TO THE OTHER HAND'S MAC ADDRESS
// uint8_t broadcastAddress[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
uint8_t broadcastAddress[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

esp_now_peer_info_t peerInfo;

struct Hand
{
  float thumb;
  float index;
  float middle;
  float ring;
  float pinky;

  float pitch;
  float roll;
  float yaw;

  float x;
  float y;
  float z;
};

Hand hand;
#ifdef RIGHT_HAND
Hand left_hand;
#endif
Finger* fingers[NUM_FINGERS];


#ifdef RIGHT_HAND
void onDataReceive(const uint8_t * mac, const uint8_t *incomingData, int len) {
  memcpy(&left_hand, incomingData, sizeof(left_hand));
}
#else
void onDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
  Serial.print("Last Packet Send Status: ");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
}
#endif

void read_hand_data() {
  hand.thumb = fingers[0]->read();
  hand.index = fingers[1]->read();
  hand.middle = fingers[2]->read();
  hand.ring = fingers[3]->read();
  hand.pinky = fingers[4]->read();
}

#ifdef RIGHT_HAND
float* get_sign_frame() {
  static float frame[22];
  frame[0] = left_hand.thumb;
  frame[1] = left_hand.index;
  frame[2] = left_hand.middle;
  frame[3] = left_hand.ring;
  frame[4] = left_hand.pinky;
  frame[5] = left_hand.pitch;
  frame[6] = left_hand.roll;
  frame[7] = left_hand.yaw;
  frame[8] = left_hand.x;
  frame[9] = left_hand.y;
  frame[10] = left_hand.z;
  frame[11] = hand.thumb;
  frame[12] = hand.index;
  frame[13] = hand.middle;
  frame[14] = hand.ring;
  frame[15] = hand.pinky;
  frame[16] = hand.pitch;
  frame[17] = hand.roll;
  frame[18] = hand.yaw;
  frame[19] = hand.x;
  frame[20] = hand.y;
  frame[21] = hand.z;

  return frame;
}
#endif

void setup(void) {

  Serial.begin(115200);
  // ================ ESP-NOW SETUP ================
  WiFi.mode(WIFI_STA);

  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }

  #ifdef RIGHT_HAND
  esp_now_register_recv_cb(onDataReceive);
  #else
  esp_now_register_send_cb(onDataSent);
  #endif

  memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  peerInfo.channel = 0;  
  peerInfo.encrypt = false;

  if (esp_now_add_peer(&peerInfo) != ESP_OK){
    Serial.println("Failed to add peer");
    return;
  }
  // ================ END ESP-NOW SETUP ================

  for (int i = 0; i < NUM_FINGERS; i++) {
    fingers[i] = new Finger(i);
  }
}

void loop() {
  read_hand_data();
  
  #ifdef RIGHT_HAND
  // Process hand data from left hand
  float* sign_frame = get_sign_frame();
  // Use sign_frame for further processing
  #else
  // Send hand data to right hand
  esp_err_t result = esp_now_send(broadcastAddress, (uint8_t *) &hand, sizeof(hand));
  #endif

  if (result == ESP_OK) {
    Serial.println("Sent with success");
  }
  else {
    Serial.println("Error sending the data");
  }

  delay(100);
}