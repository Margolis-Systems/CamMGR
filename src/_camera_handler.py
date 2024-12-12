import cv2
import threading
import os


class CamThread(threading.Thread):
    def __init__(self, cam_conf):
        threading.Thread.__init__(self)
        self.previewName = cam_conf.name
        self.camID = cam_conf.id

    def run(self):
        cam_preview(self.previewName, self.camID)


def cam_preview(previewName, camID):
    cv2.namedWindow(previewName)
    cam = cv2.VideoCapture(camID)
    frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    folder = 'test1'  # todo: FOLDER NAME
    if not os.path.exists('sessions/{}'.format(folder)):
        os.mkdir('sessions/{}'.format(folder))
    out = cv2.VideoWriter('sessions/{}/{}.mp4'.format(folder, camID), fourcc, 20.0, (frame_width, frame_height))
    if cam.isOpened():
        rval, frame = cam.read()
    else:
        rval = False

    while rval:
        cv2.imshow(previewName, frame)
        rval, frame = cam.read()
        out.write(frame)
        key = cv2.waitKey(20)
        if key == 27:  # exit on ESC
            break
    cv2.destroyWindow(previewName)
