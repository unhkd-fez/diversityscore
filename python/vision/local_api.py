import requests
import json
from .face_aligner import *

DLIB_LANDMARKS_URI = "resources/mdl/shape_predictor_68_face_landmarks.dat"

MY_TF_MODEL_URL = "https://diversifynd-model.herokuapp.com/v1/models/model/versions/3:predict"

IMAGE_SIZE = 200

class Local_API:
    def __init__(self):
        self.image_size = IMAGE_SIZE

        self.gender_categories = ['male', 'female']
        self.race_categories = ['white', 'black', 'asian', 'indian', 'others']


    def _normalize(self,x):
        """
        Normalize a list of sample image data in the range of 0 to 1
        : x: List of image data.  The image shape is (32, 32, 3)
        : return: Numpy array of normalized data
        """
        return np.array((x - np.min(x)) / (np.max(x) - np.min(x)))


    def _detect_faces(self,img):

        detector = dlib.get_frontal_face_detector()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.uint8)
        rects = detector(gray, 2)
        return rects

    def _face_detect(self, file_url=None):

        with open('resources/dummy4.json') as f:
            data = json.load(f)

        return data


    def face_detect(self, file_url=None):

        image = cv2.imread(file_url)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = image.astype(np.float32)

        # image = load_image(image_path)
        # img = Image.fromarray(image.astype('uint8'), 'RGB')
        # img.show()

        faces = self._detect_faces(image)
        predictor = dlib.shape_predictor(DLIB_LANDMARKS_URI)


        fa = FaceAligner(predictor, desiredFaceWidth=IMAGE_SIZE)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.uint8)
        instances = []
        rectangles = []
        for face in faces:
            faceAligned = fa.align(image, gray, face)
            image_aligned = np.reshape(faceAligned, (self.image_size, self.image_size, 3))

            image_aligned = self._normalize(image_aligned)

            element = {"image": image_aligned.tolist()}
            instances.append(element)

            left = face.left()
            top = face.top()
            width = face.right() - left
            height = face.bottom() - top
            rectangle = {"top": str(top), "left": str(left), "height": str(height), "width": str(width)}
            rectangles.append(rectangle)

        data_dict = {
            "instances" : instances
        }

        data = json.dumps(data_dict)

        json_response = requests.post(MY_TF_MODEL_URL, data=data)

        # Extract text from JSON
        response = json.loads(json_response.text)

        predictions = response['predictions']

        result_dict = []

        for i in range(len(faces)):
            element = {}
            gender = self.gender_categories[predictions[i]["gender"]]
            race = self.race_categories[predictions[i]["race"]]

            element["faceAttributes"] = {"gender":gender, "race":race, "race_score": predictions[i]["race_score"]}
            element["faceRectangle"] = rectangles[i]
            result_dict.append(element)

        return result_dict


## Test faces

if __name__=="__main__":

    FILE_IMAGE = "resources/img/ironhack.png"

    client = Local_API()
    faces = client.face_detect(file_url=FILE_IMAGE)