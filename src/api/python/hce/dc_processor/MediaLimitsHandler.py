"""
HCE project,  Python bindings, Distributed Tasks Manager application.
MediaLimitsHandler Class content main functional for check media limits

@package: dc_processor
@file MediaLimitsHandler.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2016 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import os
import json
import base64
import tempfile
import psutil
import requests
from PIL import Image

import app.Utils as Utils  # pylint: disable=F0401

logger = Utils.MPLogger().getLogger()

class MediaLimitsHandler(object):
  # #Constants used in class
  TEMP_FILE_SUFFIX = '.jpg'
  BINARY_IMAGE_SEARCH_STR = 'base64,'
  # types name of limits
  MEDIA_LIMITS_TYPE_NAME = 'img'


  # # Internal class for image limits properties
  class ImageLimits(object):
    # #Constants used in class
    CONTENT_TYPE_NAME = 'Content-Type'
    MIN_WIDTH_NAME = 'min_width'
    MAX_WIDTH_NAME = 'max_width'
    MIN_HEIGHT_NAME = 'min_height'
    MAX_HEIGHT_NAME = 'max_height'
    MIN_RATIO = 'min_ratio'
    MAX_RATIO = 'max_ratio'
    MIN_COLORS = 'min_colors'
    # dictionary with property names
    propertyNamesDict = {
        'contentType':CONTENT_TYPE_NAME,
        'minWidth':MIN_WIDTH_NAME,
        'maxWidth':MAX_WIDTH_NAME,
        'minHeight':MIN_HEIGHT_NAME,
        'maxHeight':MAX_HEIGHT_NAME,
        'minRatio':MIN_RATIO,
        'maxRatio':MAX_RATIO,
        'minColors':MIN_COLORS}

    def __init__(self):
      self.contentType = None
      self.minWidth = None
      self.maxWidth = None
      self.minHeight = None
      self.maxHeight = None
      self.minRatio = None
      self.maxRatio = None
      self.minColors = None


  # # Internal class for image properties
  class ImageProperty(object):
    def __init__(self):
      self.width = None
      self.height = None
      self.ratio = None
      self.colors = None
      self.format = None

  # Constructor
  # @param propertyString - contains string with json format
  def __init__(self, propertyString):
    # initialization variable content of limits structure
    self.mediaLimits = self.__getMediaLimits(self.__loadProperty(propertyString))


  # # Get media limits object
  #
  # @param propertyDict - property dict
  # @return instance of necessary type (ImageLimits...)
  def __getMediaLimits(self, propertyDict):
    # variable for result
    ret = None
    try:
      if not isinstance(propertyDict, dict):
        raise Exception("Wrong type of property: %s" % str(type(property)))

      for key, value in propertyDict.items():
        logger.debug("Enter to read property '%s'", str(key))
        if self.MEDIA_LIMITS_TYPE_NAME == key:
          if isinstance(value, dict):
            ret = self.__getImageLimits(value)
          else:
            logger.debug("Wrong type of limits: '%s'. Skipped", str(type(value)))
        else:
          logger.error("Unsupported name of limits: '%s'. Skipped", str(key))

        logger.debug("Leave to read property '%s'", str(key))

    except Exception, err:
      logger.error("Error: %s", str(err))

    return ret


  # # load property from input json
  #
  # @param propertyString - contains string with json format
  # @return object properties
  def __loadProperty(self, propertyString):
    # variable for result
    ret = None
    try:
      if propertyString is None or not isinstance(propertyString, basestring):
        raise Exception('Wrong type %s of property' % str(type(propertyString)))

      ret = json.loads(propertyString)
    except Exception, err:
      logger.error("Initialisation class '%s' was failed. Error: '%s'", self.__class__.__name__, str(err))

    return ret


  # # Get image limits property
  #
  # @param limitsDict - limits dict
  # @return ImageLimits  instance if success or othewise None
  def __getImageLimits(self, limitsDict):
    # variable for result
    imageLimits = MediaLimitsHandler.ImageLimits()

    for key, value in MediaLimitsHandler.ImageLimits.propertyNamesDict.items():
      if value in limitsDict.keys() and hasattr(imageLimits, key):
        setattr(imageLimits, key, limitsDict[value])

    return imageLimits


  # # Get image and save to file
  #
  # @param content - binary content of image
  # @return temporary file name
  def __saveImageToFile(self, content):
    # variable for result
    ret = None
    try:
      if content is None:
        raise Exception("Image content wasn't get for save on disk.")

      # save to file
      tmpf = tempfile.NamedTemporaryFile(suffix=self.TEMP_FILE_SUFFIX, delete=False)
      tmpf.file.write(content)
      tmpf.close()
      logger.debug('Image saved to file: ' + tmpf.name)
      # save name
      ret = tmpf.name
    except Exception, err:
      logger.debug("Error: %s", str(err))

    return ret


  # #Load image
  #
  # @param urlString - url string of image
  # @param binaryType - boolean flag is binary image
  # @return binary content of image
  def __loadImage(self, urlString, binaryType=False):
    # variable for result
    ret = None
    try:
      if binaryType:
        # extract binary image
        pos = urlString.find(self.BINARY_IMAGE_SEARCH_STR)
        if pos > -1:
          s = urlString[pos + len(self.BINARY_IMAGE_SEARCH_STR):]
          ret = base64.b64decode(s)
      else:
        # send get request
        res = requests.get(urlString)
        ret = res.content
    except Exception, err:
      logger.debug("Error: %s", str(err))

    return ret


  # # Get image property
  #
  # @param urlString - url string of image
  # @param binaryType - boolean flag is binary image
  # @return ImageProperty instance if success or othewise None
  def __getImageProperty(self, urlString, binaryType=False):
    # variable for result
    ret = None
    logger.debug("Url string: %s", str(urlString))
    # load image and save to file
    imageFileName = self.__saveImageToFile(self.__loadImage(urlString, binaryType))
    if imageFileName is not None:
      try:
        # open file for extract data
        imageFile = Image.open(imageFileName)
        if imageFile is None:
          raise Exception("Cannot open image file: '%s'", str(imageFileName))

        # create instance
        imageProperty = MediaLimitsHandler.ImageProperty()
        # set format of image
        imageProperty.format = imageFile.format
        # set width
        if len(imageFile.size) > 0:
          imageProperty.width = imageFile.size[0]
        # set height
        if len(imageFile.size) > 1:
          imageProperty.height = imageFile.size[1]

        if imageProperty.width > 0 and imageProperty.height > 0:
          # set ratio
          imageProperty.ratio = float(imageProperty.height) / imageProperty.width
          # set colors count
          size = imageProperty.width * imageProperty.height
          vm = psutil.virtual_memory()
          logger.debug("Image size = %s, available memory = %s", str(size), str(vm.available))
          if vm.available < size:
            logger.debug("!!! Not enough memory for get colors... Skipped")
          else:
            colors = imageFile.getcolors(size)
            if colors is not None:
              imageProperty.colors = len(colors)

        ret = imageProperty
      except Exception, err:
        logger.debug("Error: %s", str(err))
      finally:
        if os.path.isfile(imageFileName):
          os.remove(imageFileName)
          logger.debug('Remove file: %s', str(imageFileName))

    return ret


  # # check allowed limits for image
  #
  # @param imageLimits - instance of ImageLimits class
  # @param imageProperty - instance of ImageProperty class
  # @return True if allowed or otherwise False
  def __isAllowedImage(self, imageLimits, imageProperty):
    # variable for result
    ret = True
    try:
      if isinstance(imageLimits, MediaLimitsHandler.ImageLimits) and \
      isinstance(imageProperty, MediaLimitsHandler.ImageProperty):

        if imageProperty.width is not None and imageLimits.maxWidth is not None and \
        int(imageProperty.width) > int(imageLimits.maxWidth):
          raise Exception("Parameter 'width' has not allowed value: %s > %s" % \
                          (str(imageProperty.width), str(imageLimits.maxWidth)))

        if imageProperty.width is not None and imageLimits.minWidth is not None and \
        int(imageProperty.width) < int(imageLimits.minWidth):
          raise Exception("Parameter 'width' has not allowed value: %s < %s" % \
                          (str(imageProperty.width), str(imageLimits.minWidth)))

        if imageProperty.height is not None and imageLimits.maxHeight is not None and \
        int(imageProperty.height) > int(imageLimits.maxHeight):
          raise Exception("Parameter 'height' has not allowed value: %s > %s" % \
                          (str(imageProperty.height), str(imageLimits.maxHeight)))

        if imageProperty.height is not None and imageLimits.minHeight is not None and \
        int(imageProperty.height) < int(imageLimits.minHeight):
          raise Exception("Parameter 'height' has not allowed value: %s < %s" % \
                          (str(imageProperty.height), str(imageLimits.minHeight)))

        if imageProperty.ratio is not None and imageLimits.maxRatio is not None and \
        float(imageProperty.ratio) > float(imageLimits.maxRatio):
          raise Exception("Parameter 'ratio' has not allowed value: %s > %s" % \
                          (str(imageProperty.ratio), str(imageLimits.maxRatio)))

        if imageProperty.ratio is not None and imageLimits.minRatio is not None and \
        float(imageProperty.ratio) < float(imageLimits.minRatio):
          raise Exception("Parameter 'ratio' has not allowed value: %s < %s" % \
                          (str(imageProperty.ratio), str(imageLimits.minRatio)))

        if imageProperty.colors is not None and imageLimits.minColors is not None and \
        int(imageProperty.colors) < int(imageLimits.minColors):
          raise Exception("Parameter 'colors' has not allowed value: %s < %s" % \
                          (str(imageProperty.colors), str(imageLimits.minColors)))

        if imageProperty.format is not None and imageLimits.contentType is not None and \
        isinstance(imageProperty.format, basestring) and isinstance(imageLimits.contentType, list):
          if not imageProperty.format.lower() in \
            [contentTypeName.lower() for contentTypeName in imageLimits.contentType]:
            raise Exception("Parameter 'format' = '%s' has not allowed value by '%s' =  %s" % \
                            (str(imageProperty.format),
                             str(MediaLimitsHandler.ImageLimits.propertyNamesDict['contentType']),
                             str(imageLimits.contentType)))

    except Exception, err:
      logger.debug("%s", str(err))
      ret = False

    return ret


  # # Dump object variables to logger
  #
  # @param obj - object instance
  # @return - None
  def __dumpObj(self, obj):
    msg = 'Instance %s has:' % (str(type(obj)))
    if obj is not None:
      for name, value in obj.__dict__.items():
        msg += ("\n'%s' = %s") % (str(name), str(value))
    logger.debug(msg)


  # # Check allowed limits
  #
  # @param urlString - url string of image
  # @param binaryType - boolean flag is binary image
  # @return True if allowed or otherwise False
  def isAllowedLimits(self, urlString, binaryType=False):
    # variable for result
    ret = True

    if self.mediaLimits is not None:
      if isinstance(self.mediaLimits, MediaLimitsHandler.ImageLimits):
        # Get image property
        imageProperty = self.__getImageProperty(urlString, binaryType)
        if imageProperty is None:
          ret = False
        else:
          # Dump objects
          self.__dumpObj(self.mediaLimits)
          self.__dumpObj(imageProperty)

          # Check image limits
          ret = self.__isAllowedImage(self.mediaLimits, imageProperty)
      else:
        pass  # reserved for other types

    return ret
