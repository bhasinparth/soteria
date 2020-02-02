import time
import edgeiq
import face_recognition
import requests
import cv2
from firebase import firebase
"""
Use object detection to detect human faces in the frame in realtime.

To change the computer vision model, follow this guide:
https://dashboard.alwaysai.co/docs/application_development/changing_the_model.html

To change the engine and accelerator, follow this guide:
https://dashboard.alwaysai.co/docs/application_development/changing_the_engine_and_accelerator.html
"""
def cb():
  print("Video saved")

def main():
    facial_detector = edgeiq.ObjectDetection(
            "alwaysai/res10_300x300_ssd_iter_140000")
    facial_detector.load(engine=edgeiq.Engine.DNN)

    print("Engine: {}".format(facial_detector.engine))
    print("Accelerator: {}\n".format(facial_detector.accelerator))
    print("Model:\n{}\n".format(facial_detector.model_id))

    fps = edgeiq.FPS()
    event_video_writer = edgeiq.EventVideoWriter(pre_roll=3, post_roll=3, fps=1)

    try:
        with edgeiq.WebcamVideoStream(cam=0) as webcam, \
                edgeiq.Streamer() as streamer:
            # Allow webcam to warm up
            time.sleep(2.0)
            fps.start()

            i=0
            face_dict = {0: "Vignesh", 1: "Parth", 2: "Rosna", 3: "Vipul"}

            fireb = firebase.FirebaseApplication('https://soteria-hacksc.firebaseio.com/', None)
            fire_res = fireb.get('/faces_detected', None)
            print(fire_res)
            tflag = False

            # loop detection
            while True:
                frame = webcam.read()
                event_video_writer.update(frame)
                # detect human faces
                results = facial_detector.detect_objects(
                        frame, confidence_level=.5)
                frame = edgeiq.markup_image(
                        frame, results.predictions, show_labels=False)

                # Generate text to display on streamer
                text = ["Model: {}".format(facial_detector.model_id)]
                text.append(
                        "Inference time: {:1.3f} s".format(results.duration))
                text.append("Faces:")

                bb_img_list = []

                for prediction in results.predictions:
                    text.append("{:2.2f}%".format(prediction.confidence * 100))
                    bbox = prediction.box
                    bb_image = edgeiq.cutout_image(frame,bbox)
                    bb_img_list.append(bb_image)

                try :
                    cv2.imwrite('./unknown_'+str(i)+'.jpg',bb_img_list[0])
                    unknown_image = face_recognition.load_image_file("./unknown_"+str(i)+".jpg")
                    unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
                except :
                    unknown_image = face_recognition.load_image_file("./unknown.jpg")
                    unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
                    print("Unknown face!!")
                    
                j = 0                
                while j<4:
                    known_image = face_recognition.load_image_file("./"+str(j)+".jpg")
                    biden_encoding = face_recognition.face_encodings(known_image)[0]
                    
                    if face_recognition.compare_faces([biden_encoding], unknown_encoding)[0]:
                        print("Face recognised: ", j)
                        text.append("Recognised: ")
                        text.append(face_dict[j])
                        fire_data = {i: {'id': face_dict[j], 'location': '34.020091, -118.286119'}}
                        fire_result = fireb.post('/faces_detected', fire_data)
                        print(fire_result)

                    j += 1


                alert_res = fireb.get('/alert', None)
                if not tflag and alert_res['bool'] == 1:
                    print("Alert!!")
                    text.append("Alert!!! Potential Imminent Danger around you")
                    output_path="video_clip.avi"
                    event_video_writer.start_event(output_path=output_path, callback_function=cb)
                    timeout = time.time() + 30
                    tflag = True

                if tflag and time.time() > timeout:
                    print(fps.compute_fps())
                    print("Video complete!")
                    event_video_writer.finish_event()
                    timeout = time.time() + 60*5


                streamer.send_data(frame, text)
                # streamer.send_data(bb_img_list[0], text)

                fps.update()
                i += 1

                if streamer.check_exit():
                    break

    finally:
        # stop fps counter and display information
        fps.stop()
        print("[INFO] elapsed time: {:.2f}".format(fps.get_elapsed_seconds()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.compute_fps()))

        print("Program Ending")


if __name__ == "__main__":
    main()
