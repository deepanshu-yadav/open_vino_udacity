"""
Helper classs for starting a separate thread for reading frame from the Camera
Device
"""

import cv2
from threading import Thread
import numpy as np
class VideoStream:
    """ Camera object that controls
        video streaming from the Camera
    """

    def __init__(self, resolution=(640, 480), framerate=30, source=0):
        # Initialize the PiCamera and the camera image stream

        self.stream = cv2.VideoCapture(source)
        ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        ret = self.stream.set(3, resolution[0])
        ret = self.stream.set(4, resolution[1])

        # Read first frame from the stream
        (self.grabbed, self.frame) = self.stream.read()

        # Variable to control when the camera is stopped
        self.stopped = False

    def start(self):
        # Start the thread that reads frames from the video stream
        Thread(target=self.update, args=(), name="Reader Thread").start()
        return self

    def update(self):
        # Keep looping indefinitely until the thread is stopped
        while True:
            # If the camera is stopped, stop the thread
            if self.stopped:
                # Release camera resources

                self.stream.release()

                return

            # Otherwise, grab the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # Return the most recent frame
        return self.frame

    def stop(self):
        # Indicate that the camera and thread should be stopped
        self.stopped = True


def camera_loop(**kwargs):
    """ Main function that keeps on fetching frame ,
        performing inference and drawing the result of
        inference on the detection window.
         Args:
           Keyword Arguements -> Each one is listed below
         Returns:
           None
         Raises:
           Raises exception if unable to draw the frame on the the window.
    """



    # Note : The object contents may change if plugin_reconfigure is called
    # thats why the inference object in the loop is global

    # these variables are used for calculation of frame per seconds (FPS)
    frame_rate_calc = 1
    freq = cv2.getTickFrequency()

    source = kwargs['source']

    camera_height = 480
    camera_width = 640

    # Initialize the stream object and start the thread that keeps on reading frames
    # This thread is independent of the Camera Processing Thread
    videostream = VideoStream(resolution=(camera_width, camera_height), source=source).start()

    # creating a window with a name
    window_name = 'Give commands by hand'
    cv2.namedWindow(window_name)

    while (True):
        # Capture frame-by-frame
        t1 = cv2.getTickCount()


        # # we need the height , width to resize the image for feeding into the model
        # height_for_model = inference.height_for_model
        # width_for_model = inference.width_for_model
        #
        # #  check if floating point model is used or not
        # floating_model = inference.floating_model
        #
        # # The minimum confidence to threshold the detections obtained from model
        # min_conf_threshold = inference.min_conf_threshold
        #
        # # The list of labels of the supported objects detected by the plugin
        # labels = inference.labels

        # Taking the frame the stream
        frame1 = videostream.read()

        frame = frame1.copy()

        # BGR to RGB
        #frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # resizing it to feed into model
        #frame_resized = cv2.resize(frame_rgb, (width_for_model, height_for_model))
        # input_data will now become 4 dimensional
        #input_data = np.expand_dims(frame_resized, axis=0)
        # now it will have (batchsize , height , width , channel)

        # Normalize pixel values if using a floating model
        # (i.e. if model is non-quantized)


        # # Perform the actual detection by running the model with the image as input
        # boxes, classes, scores = inference.perform_inference(input_data)
        #
        # # we could have got  number of objects
        # # but it does not work most of the times.
        #
        # # num = interpreter.get_tensor(output_details[3]['index'])[0]  #
        # # Total number of detected objects (inaccurate and not needed)
        #
        # # The readings array to be inserted in the readings table
        # objs = []
        #
        # # Loop over all detections and draw detection box
        # #  if confidence is above minimum then  only
        # #  that detected object will  be considered
        #
        # # The index of person class is zero.
        # for i in range(len(scores)):
        #     if ((scores[i] > min_conf_threshold) and (int(classes[i] == 0))):
        #         # Get bounding box coordinates and draw box
        #         # Interpreter can return coordinates that are outside of image dimensions,
        #         # need to force them to be within image using max() and min()
        #
        #         ymin_model = round_to_three_decimal_places(boxes[i][0])
        #         xmin_model = round_to_three_decimal_places(boxes[i][1])
        #         ymax_model = round_to_three_decimal_places(boxes[i][2])
        #         xmax_model = round_to_three_decimal_places(boxes[i][3])
        #
        #         # map the bounding boxes from model to the window
        #         ymin = int(max(1, (ymin_model * camera_width)))
        #         xmin = int(max(1, (xmin_model * camera_height)))
        #         ymax = int(min(camera_width, (ymax_model * camera_width)))
        #         xmax = int(min(camera_height, (xmax_model * camera_height)))
        #
        #         # draw the rectangle on the frame
        #         cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (10, 255, 0), 2)
        #
        #         # Contructing the label
        #
        #         # Look up object name from "labels" array using class index
        #         object_name = labels[int(classes[i])]
        #
        #         # Example: 'person: 72%'
        #         label = '%s: %d%%' % (object_name, int(scores[i] * 100))
        #
        #         # Get font size
        #         labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX,
        #                                               0.7, 2)
        #
        #         # Make sure not to draw label too close to top of window
        #         label_ymin = max(ymin, labelSize[1] + 10)
        #
        #         # Draw white box to put label text in
        #         cv2.rectangle(frame, (xmin, label_ymin - labelSize[1] - 10),
        #                       (xmin + labelSize[0], label_ymin + baseLine - 10),
        #                       (255, 255, 255), cv2.FILLED)
        #
        #         # Draw the text label
        #         cv2.putText(frame, label, (xmin, label_ymin - 7),
        #                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        #
        #         # the readings to be inserted into the table
        #         objs.append({'label': labels[classes[i]],
        #                      'score': 100 * scores[i],
        #                      'bounding_box': [xmin, ymin, xmax, ymax]
        #                      })
        #
        # # Draw framerate in corner of frame
        # cv2.putText(frame, 'FPS: {0:.2f}'.format(frame_rate_calc),
        #             (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0)
        #             , 2, cv2.LINE_AA)
        #
        # # All the results have been drawn on the frame, so it's time to display it.
        # global shutdown_in_progress
        # if shutdown_in_progress:
        #
        #     videostream.stop()
        #     time.sleep(3)
        #     cv2.destroyWindow(window_name)
        #     break
        # else:
        #
        #     # Calculate framerate
        #     t_end = cv2.getTickCount()
        #     time1 = (t_end - t1) / freq
        #     frame_rate_calc = 1 / time1
        #
        #     # readings for the reading table
        #     reads = {
        #         'count': len(objs),
        #         'objects': objs
        #     }
        #     data = {
        #         'asset': asset_name,
        #         'timestamp': utils.local_timestamp(),
        #         'key': str(uuid.uuid4()),
        #         'readings': reads
        #     }
        #     if not shutdown_in_progress:
        #         async_ingest.ingest_callback(c_callback, c_ingest_ref, data)

            # show the frame on the window
        try:
            cv2.imshow(window_name, frame)
        except Exception as e:
            print(e)
        # wait for 1 milli second
        cv2.waitKey(1)