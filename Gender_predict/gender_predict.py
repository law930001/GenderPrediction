# import os
# from azure.cognitiveservices.vision.face import FaceClient
# from msrest.authentication import CognitiveServicesCredentials
# from azure.cognitiveservices.vision.face.models import FaceAttributeType

# class GenderPredictor():

#     def __init__(self):

#         # This key will serve all examples in this document.
#         self.KEY = "e6c4e4c782e246a7a602a41fad035efd"

#         # This endpoint will be used in all examples in this quickstart.
#         self.ENDPOINT = "https://smm.cognitiveservices.azure.com/"


#     def process(self, url):

#         # Create an authenticated FaceClient.
#         face_client = FaceClient(self.ENDPOINT, CognitiveServicesCredentials(self.KEY))

#         # Detect a face in an image that contains a single face
#         single_face_image_url = url
#         single_image_name = os.path.basename(single_face_image_url)
#         # We use detection model 3 to get better performance.
#         #detected_faces = face_client.face.detect_with_url(url=single_face_image_url, detection_model='detection_01',returnFaceAttributes='gender')
#         detected_faces = face_client.face.detect_with_url(url=single_face_image_url, detection_model='detection_01',return_face_attributes=[FaceAttributeType.gender])

#         if not detected_faces:
#             return None
#             # raise Exception('No face detected from image {}'.format(single_image_name))

#         return str(detected_faces[0].face_attributes.gender).split('.')[1]

# if __name__ == '__main__':
#     gp = GenderPredictor()
#     url = 'https://a.ksd-i.com/a/2019-11-04/121569-786164.jpg'
#     print(gp.process(url))


#A Gender and Age Detection program by Mahesh Sawant
from deepface import DeepFace

import urllib.request
import os
import cv2

class GenderPredictor():

    def __init__(self):

        faceProto="./Gender_predict/protofile/opencv_face_detector.pbtxt"
        faceModel="./Gender_predict/protofile/opencv_face_detector_uint8.pb"
        ageProto="./Gender_predict/protofile/age_deploy.prototxt"
        ageModel="./Gender_predict/protofile/age_net.caffemodel"
        genderProto="./Gender_predict/protofile/gender_deploy.prototxt"
        genderModel="./Gender_predict/protofile/gender_net.caffemodel"

        self.MODEL_MEAN_VALUES=(78.4263377603, 87.7689143744, 114.895847746)
        self.ageList=['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
        self.genderList=['Male','Female']

        self.faceNet=cv2.dnn.readNet(faceModel,faceProto)
        self.ageNet=cv2.dnn.readNet(ageModel,ageProto)
        self.genderNet=cv2.dnn.readNet(genderModel,genderProto)


    def highlightFace(self, net, frame, conf_threshold=0.7):
        frameOpencvDnn=frame.copy()
        frameHeight=frameOpencvDnn.shape[0]
        frameWidth=frameOpencvDnn.shape[1]
        blob=cv2.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], True, False)

        net.setInput(blob)
        detections=net.forward()
        faceBoxes=[]
        for i in range(detections.shape[2]):
            confidence=detections[0,0,i,2]
            if confidence>conf_threshold:
                x1=int(detections[0,0,i,3]*frameWidth)
                y1=int(detections[0,0,i,4]*frameHeight)
                x2=int(detections[0,0,i,5]*frameWidth)
                y2=int(detections[0,0,i,6]*frameHeight)
                faceBoxes.append([x1,y1,x2,y2])
                cv2.rectangle(frameOpencvDnn, (x1,y1), (x2,y2), (0,255,0), int(round(frameHeight/150)), 8)
        return frameOpencvDnn,faceBoxes

    def download_image(self, url):
        urllib.request.urlretrieve(url, 'temp.jpg')


    def process(self, url, index):
        
        try:
            self.download_image(url)
        except:
            return None

        return self.predict(index)


    def predict(self, index):


        frame = cv2.imread('temp.jpg')

        padding=20

        resultImg,faceBoxes=self.highlightFace(self.faceNet,frame)

        if len(faceBoxes) == 1:


            # predict first
            for faceBox in faceBoxes:
                face=frame[max(0,faceBox[1]-padding):
                            min(faceBox[3]+padding,frame.shape[0]-1),max(0,faceBox[0]-padding)
                            :min(faceBox[2]+padding, frame.shape[1]-1)]
                try:
                    blob=cv2.dnn.blobFromImage(face, 1.0, (227,227), self.MODEL_MEAN_VALUES, swapRB=False)
                except:
                    return None
                self.genderNet.setInput(blob)
                genderPreds=self.genderNet.forward()
                gender_1=self.genderList[genderPreds[0].argmax()]


            # predict twice


            try:
                obj = DeepFace.analyze(img_path = "temp.jpg", actions = ['gender'])
            except: # except for no face detected
                return None

            gender_2 = 'Male' if obj["gender"] == 'Man' else 'Female'


            if gender_1 == gender_2:

                # os.replace('./temp.jpg', "./Gender_predict/" + gender_1 + '/' + str(index)+'.jpg')

                return gender_1
            
            else:
                return None

        # if face detected > 1
        else:
            return None



