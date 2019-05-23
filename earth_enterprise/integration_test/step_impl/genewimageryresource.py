from getgauge.python import step, before_scenario, Messages
import os, random, fnmatch, subprocess, datetime
from subprocess import Popen
import shutil

# ------------------------
# Helpful Not-Step Methods
# ------------------------
def get_env_value(sKey):
   return os.getenv(sKey, "unset")

def doesKhassetFileExist(sPathUntilDotKiasset):
   return os.path.exists(sPathUntilDotKiasset + ".kiasset/khasset.xml" )

def resetAssets():
   sCommandToRun = "/workdir/geoplatform/test/regression/States/Purge_Assets.sh > /dev/null"
   pHandle = subprocess.Popen(sCommandToRun, shell=True)
   assert (pHandle.wait() == 0)
   sCommandToRun = "/workdir/geoplatform/test/regression/States/Set_Assets.sh > /dev/null"
   pHandle = subprocess.Popen(sCommandToRun, shell=True)
   assert (pHandle.wait() == 0)

def executeCommand(sTestDir):
   sImageryRoot = "/opt/google/share/tutorials/fusion/";
   sImageryFile = "Imagery/bluemarble_4km.tif"
   
   # What if the Imagery wasn't downloaded
   sCommandToRun = "sudo " + sImageryRoot + "download_tutorial.sh >/dev/null 2>/dev/null"
   pHandle = subprocess.Popen(sCommandToRun, shell=True)
   assert (pHandle.wait() == 0)
   
   sCommandUnderTest = "/opt/google/bin/genewimageryresource"
   sCommand = sCommandUnderTest + " -o \"" + sTestDir + "\" " + sImageryRoot + sImageryFile + " 2>/dev/null"
   pHandle = subprocess.Popen(sCommand, shell=True)
   # Reason for the wait or poll is: if the process started but it returned FAILURE (example incorrect input, and the executable returned a non-zero response, the wait would have failed.
   assert ( (pHandle.wait() == 0) or (pHandle.poll() != None) )


# ------------------------
# Helpful ENV settings
# ------------------------
HOME = get_env_value("HOME")
outputDirectoryForTest = "genewimageryresourceTestOutput"
outputROOT = "/gevol/assets"

sCommandScript = "./step_impl/balaOutputPathTestDriver.sh "

# ---------------------------
# The Tests
# ------------------------
@step("reset all assets")
def resetAllAssets() :
   resetAssets ()

@step("perform ge new imagery resource simple test")
def genewimageryresourceSimpleTest() :
   testDir = outputDirectoryForTest
   executeCommand(testDir)
   assert (doesKhassetFileExist(outputROOT+"/"+testDir) == True)

@step("perform ge new imagery resource multi level directory test")
def genewimageryresourceMultiLevelDirectoryTest() :
   testDir = outputDirectoryForTest + "/dir1/dir2/dir3_prefix"
   executeCommand(testDir)
   assert (doesKhassetFileExist(outputROOT+"/"+testDir) == True)

# The directory traversal should have not been feasible:
# Reason: We do not allow directories to start with "/".  So, allowing this will subvert the feature.
@step("perform ge new imagery resource directory traversal test")
def genewimageryresourceDirectoryTraversal() :
   # Although it is supposed to be written into /gevol/asset, can I please try /gevol/src?
   testDir = "../../../../../gevol/src/" + outputDirectoryForTest
   executeCommand(testDir)
   assert (doesKhassetFileExist(testDir) == False), " Performing directory traversal and writing somewhere else should not be possible"

@step("perform ge new imagery resource root directory test")
def genewimageryresourceDirStartsAtRoot() :
   testDir = "/gevol/assets/" + outputDirectoryForTest
   executeCommand(testDir)
   assert (doesKhassetFileExist(testDir) == False)

@step("perform ge new imagery resource having unacceptable characters test")
def genewimageryresourceHavingUnacceptableCharacters() :
   testDir = outputDirectoryForTest + "whatever:-$else"
   executeCommand(testDir)
   assert (doesKhassetFileExist(outputROOT+"/"+testDir) == False)

@step("perform ge new imagery resource having unspecified special characters test")
def genewimageryresourceUnspecifiedSpecialCharacters() :
   testDir = outputDirectoryForTest + 'TEMP/VAL\tUE'
   executeCommand(testDir)
   assert (doesKhassetFileExist(outputROOT+"/"+testDir) == False), " Creating Files and Dirs with TAB char should not have been allowed!"

@step("perform ge new imagery resource having empty directory test")
def genewimageryresourceNegativeCaseEmptyDir() :
   testDir = ""
   executeCommand(testDir)
   assert (doesKhassetFileExist(outputROOT+"/"+testDir) == False)

