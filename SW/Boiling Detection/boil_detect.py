from skimage.measure import compare_ssim
import cv2
import numpy as np
import time


class BoilDetector:

    def __init__self(self):
        self.MIN_BOILING_TEMP = 170 # temp considered to be boiling
        self.frames_elapsed = 0 # frames that have passed
        self.frame_frequency = 1 # frequency of frames being compared
        self.thresh = 0.985 # thresh to boil
        self.SSIM_count = 5 # how often median will be found

        self.median_SSIM = [[],[],[],[]] # SSIMS recorded until median is found
        self.boiling = [] # boiling list holding median SSIMs found
        self.start_boiling = [0,0,0,0] # times each burner started boiling
        self.began_boiling = [False,False,False,False] # if each burner has been detected to be boiling
        self.masks = [] # mask used for each burner

        self.last_image = None
        self.current_image = None
        self.last_quads = [None,None,None,None]
        self.current_quads = [None,None,None,None]

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

    def __initialize_masks(self,burners):
        """
        Refreshes mask if a pot is newly detected on the burners.
        :param burners: Stove burners
        """
        masks = self.masks
        for mask,burner,quad in zip(masks,burners,self.last_quads):
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
        # updates frames_elapsed
        self.frames_elapsed = self.frames_elapsed + 1
        burners = stove.get_burners()

        # creates new masks if a pot was added
        self.initialize_masks(burners)

        # if program has not executed before
        if self.last_image is None:
            self.last_image = frame
            self.last_quads = self.__split_frame(self.last_image)

        # if the number of frames that have been processed are desired amount, proceed
        elif self.frames_elapsed == self.frame_frequency:
            # if there is no second image recorded yet
            if self.current_image is None:
                self.current_image = frame
                self.current_quads = self.__split_frame(self.current_image)
            # second image does exist, must shift images
            else:
                self.last_image = self.current_image
                self.current_image = frame

            # splits the frames
            self.last_quads = self.__split_frame(self.last_image)
            self.current_quads = self.__split_frame(self.current_image)

            # Detects boiling on active burners
            curr_idx = 0 # index corresponding to current burner
            for burner in burners:
                # if there is a pot on burner
                if burner.pot_detected:
                    mask = self.masks[curr_idx]
                    score = self.___get_score(mask, self.last_quads[curr_idx], self.current_quads[curr_idx])
                    self.median_SSIM[curr_idx].append(score)

                    # median is calculated when enough SSIMs have been recorded
                    if len(self.median_SSIM[curr_idx]) == self.SSIM_count:
                        med = np.median(self.median_SSIM[curr_idx])
                        self.boiling[curr_idx].append(med)
                        self.median_SSIM[curr_idx].clear()

                    # ensures that the boiling list is not empty before trying to calculate status
                    if len(self.boiling[curr_idx]) > 0:
                        # waits to set boiling flag until 30 seconds has passed and the began_boiling flag remains true
                        if self.began_boiling[curr_idx] and time.time() - self.start_boiling[curr_idx] >= 30:
                            burner.boiling = True
                        elif self.began_boiling[curr_idx]:
                            self.began_boiling[curr_idx] = self.__check_boiling(self.boiling[curr_idx], self.thresh)
                            # if beganBoiling becomes false, resets the flag
                            if not self.began_boiling[curr_idx]:
                                self.start_boiling[curr_idx] = time.time()  # sets time to when it began boiling
                        else:
                            self.began_boiling[curr_idx] = self.__check_boiling(self.boiling[curr_idx], self.thresh)
                            self.start_boiling[curr_idx] = time.time() # keeps track of time when started boiling
                            if self.began_boiling[curr_idx] or time.time() >= 30:
                                self.boiling[curr_idx].clear()  # clear the boiling list for new values to be collected
                curr_idx = curr_idx + 1

        # sets appropriate stove burners to boiling
        for burner in burners:
            if burner.boiling and burner.temp >= self.MIN_BOILING_TEMP:
                burner.boiling = True # keeps True value
            else:
                burner.boiling = False # changes if temp not high enough
