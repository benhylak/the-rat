from skimage.measure import compare_ssim
import cv2
import numpy as np
import time


class BoilDetector:

    def __init__self(self):
        self.temp = 170 # temp considered to be boiling
        self.frame_count = 0 # frames that have passed
        self.count = 1 # frequency of frames being compared
        self.thresh = 0.985 # thresh to boil
        self.SSIM_count = 5 # how often median will be found

        self.median_SSIM = [[],[],[],[]] # SSIMS recorded until median is found
        self.boiling = [] # boiling list holding median SSIMs found
        self.start_boiling = [0,0,0,0] # times each burner started boiling
        self.began_boiling = [False,False,False,False] # if each burner has been detected to be boiling
        self.masks = [] # mask used for each burner

        self.first_image = None
        self.second_image = None
        self.first_quads = [None,None,None,None]
        self.second_quads = [None,None,None,None]

    def __compare_images(self, gray1, gray2):
        """
        Compute the Structural Similarity Index (SSIM) between the two
        images, ensuring that the SSIM is returned
        :param gray1: grayscale image
        :param gray2: grayscale image
        :return: SSIM score between two images between 0 and 1
        """
        (score, diff) = compare_ssim(gray1, gray2, full=True)
        diff = (diff * 255).astype("uint8")

        return score

    def __create_mask(self, img):
        """
        Returns a mask with the cut out ellipse to be used in all iterations.
        Created using the input image after calculating ellipse.
        :param img: Image off which ellipse is based
        :return: Mask to be used for the image
        """
        copy = img.copy()
        gray_img = cv2.cvtColor(copy, cv2.COLOR_BGR2GRAY)

        # increase the contrast in the image
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl1 = clahe.apply(gray_img)

        # create a black mask
        mask = np.zeros_like(gray_img)

        # thresh
        (thresh, im_bw) = cv2.threshold(cl1, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # find contours
        contours, _ = cv2.findContours(im_bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # sort the contours from largest area to smallest, get the largest contour
        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
        cnt = sorted_contours[0]

        # fit an ellipse to the largest contour
        ellipse = cv2.fitEllipse(cnt)
        # Unpack the properties of the returned ellipse
        x = int(ellipse[0][0])  # x coordinate of the center
        y = int(ellipse[0][1])  # y coordinate of the center
        a = int(ellipse[1][0] / 2)  # major semi-axis
        b = int(ellipse[1][1] / 2)  # minor semi-axis
        theta = int(ellipse[2])  # rotation angle

        # draw the found ellipse onto the mask
        cv2.ellipse(mask, (x, y), (a, b), theta, 0, 360, ((255, 255, 255)), -1)
        return mask

    def __apply_mask(self, img, mask):
        """
        Applies the given mask to the input image.
        :param img: Image to be masked
        :param mask: Mask to be used
        :return: A masked version of the image
        """
        copy = img.copy()
        return cv2.bitwise_and(copy, copy, mask=mask)

    def __split_frame(self, frame):
        """
        Takes input frame and splits it into 4 equal quadrants.
        Best bet so far would be to take in distorted frame.
        :param frame: Frame to be split.
        :return: Four images representing the split frame.
        """
        height, width = frame.shape[:2]
        center_col = int(width / 2)
        center_row = int(height / 2)

        first_quad = frame[0:center_row, 0:center_col]
        second_quad = frame[0:center_row, center_col:width]
        third_quad = frame[center_row:height, 0:center_col]
        fourth_quad = frame[center_row:height, center_col:width]

        return [first_quad, second_quad, third_quad, fourth_quad]

    def ___get_score(self, mask, quad1, quad2):
        """
        Helper function to return SSIM score between two images
        :param mask: Mask to be applied to image
        :param quad1: First image quadrant being compared
        :param quad2: Second image quadrant
        :return:
        """
        masked1 = self.__apply_mask(quad1, mask)
        masked2 = self.__apply_mask(quad2, mask)

        # converts the masked images images to grayscale
        gray1 = cv2.cvtColor(masked1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(masked2, cv2.COLOR_BGR2GRAY)

        # compare the two images
        return self.__compare_images(gray1, gray2)

    def __check_boiling(boiling, thresh):
        """
        Checks to see if the past values recorded in boiling
        average out to be less than a given boiling threshhold.
        :param boiling: List containing an X number of median SSIM's
        :param thresh: Value signaling if average has fallen beneath certain boiling thresh
        :return: Boolean signaling if the input list values indicate boiling
        """
        average = sum(boiling) / len(boiling)
        if average < thresh:
            return True
        else:
            return False

    def __burners(self,stove):
        """
        Returns a list of the Burners in the Stove object
        :param stove: Stove object
        :return: List of the burners
        """
        burners = []
        burners.append(stove.upper_left)
        burners.append(stove.upper_right)
        burners.append(stove.lower_left)
        burners.append(stove.lower_right)
        return burners

    def __initialize_masks(self,burners):
        """
        Refreshes mask if a pot is newly detected on the burners.
        :param burners: Stove burners
        """
        masks = self.masks
        for mask,burner,quad in zip(masks,burners,self.first_quads):
            # mask never made before
            if mask is None and quad is not None and burner.pot_detected:
                self.masks.append(self.__create_mask(quad))
            # if pot no longer detected resets the mask
            elif burner.pot_detected is False:
                idx = masks.index(mask)
                self.masks[idx] = None

    def update(self, frame, stove):
        """
        Takes an input frame and updates the boiling state of the burners.
        :param frame: Input frame used to update boiling status
        :param stove: Stove object holding current stove state
        """
        # updates frame_count
        self.frame_count = self.frame_count + 1
        burners = self.__burners(stove)

        # creates new masks if a pot was added
        self.initialize_masks(burners)

        # if program has not executed before
        if self.first_image is None:
            self.first_image = frame
            self.first_quads = self.__split_frame(self.first_image)

        # if the number of frames that have been processed are desired amount, proceed
        elif self.frame_count == self.count:
            # if there is no second image recorded yet
            if self.second_image is None:
                self.second_image = frame
                self.second_quads = self.__split_frame(self.second_image)
            # second image does exist, must shift images
            else:
                self.first_image = self.second_image
                self.second_image = frame

            # splits the frames
            self.first_quads = self.__split_frame(self.first_image)
            self.second_quads = self.__split_frame(self.second_image)

            # Detects boiling on active burners
            i = 0
            for burner in burners:
                # if there is a pot on burner
                if burner.pot_detected:
                    mask = self.masks[i]
                    score = self.___get_score(mask, self.first_quads[i], self.second_quads[i])
                    self.median_SSIM[i].append(score)

                    # median is calculated when enough SSIMs have been recorded
                    if len(self.median_SSIM[i]) == self.SSIM_count:
                        med = np.median(self.median_SSIM[i])
                        self.boiling[i].append(med)
                        self.median_SSIM[i].clear()

                    # ensures that the boiling list is not empty before trying to calculate status
                    if len(self.boiling[i]) > 0:
                        # waits to set boiling flag until 30 seconds has passed and the began_boiling flag remains true
                        if self.began_boiling[i] and time.time() - self.start_boiling[i] >= 30:
                            burner.boiling = True
                        elif self.began_boiling[i]:
                            self.began_boiling[i] = self.__check_boiling(self.boiling[i], self.thresh)
                            # if beganBoiling becomes false, resets the flag
                            if not self.began_boiling[i]:
                                self.start_boiling[i] = time.time()  # sets time to when it began boiling
                        else:
                            self.began_boiling[i] = self.__check_boiling(self.boiling[i], self.thresh)
                            self.start_boiling[i] = time.time() # keeps track of time when started boiling
                            if self.began_boiling[i] or time.time() >= 30:
                                self.boiling[i].clear()  # clear the boiling list for new values to be collected
                i = i + 1

        # sets appropriate stove burners to boiling
        if burners[0].boiling and stove.upper_left.temp >= self.temp:
            stove.upper_left = True
        if burners[1].boiling and stove.upper_right.temp >= self.temp:
            stove.upper_right = True
        if burners[2].boiling and stove.lower_left.temp >= self.temp:
            stove.lower_left = True
        if burners[3].boiling and stove.lower_right.temp >= self.temp:
            stove.lower_right = True