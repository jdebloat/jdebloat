#!/usr/bin/env stack
-- stack --resolver lts-12.11 script

{-# LANGUAGE RecordWildCards #-}
{-# LANGUAGE ScopedTypeVariables #-}
import Development.Shake
import Development.Shake.Command
import Development.Shake.FilePath
import Development.Shake.Util

import qualified Data.List as List

import System.Directory (makeAbsolute)

-- cassava
import Data.Csv as Csv

-- bytestring
import qualified Data.ByteString.Lazy as BL

-- vector
import qualified Data.Vector as V

-- prelude
import Data.Foldable

main :: IO ()
main = do
  Right (vector :: V.Vector BenchmarkDesc) <- Csv.decode HasHeader <$> BL.readFile "data/benchmarks.csv"
  let benchmarks = V.toList vector
  let targets = ["initial", "initial+jreduce", "initial+inliner", "initial+jshrink"]
  let all = [
        "initial",
        "initial+jreduce", "initial+inliner", "initial+jshrink",
        "initial+inliner+jreduce+jshrink",
        "initial+inliner+jshrink+jreduce",
        "initial+jreduce+inliner+jshrink",
        "initial+jreduce+jshrink+inliner",
        "initial+jshrink+inliner+jreduce",
        "initial+jshrink+jreduce+inliner"
        ]
  shakeArgs shakeOptions
    { shakeFiles="output"
    , shakeLint=Just LintBasic
    , shakeThreads=0
    , shakeReport=["output/build.json", "output/build.html", "output/build.trace"]
    , shakeTimings=True
    , shakeProgress=progressSimple
    } $ do
    want ["output/report.csv"]

    --phony "clean" $ do
        --putNormal "Cleaning files in output"
        --removeFilesAfter "output" ["//*"]
    
    --phony "setup" $ do
        --putNormal "Setting up database"
        --cmd_ (Cwd "tools/inliner") "make setup"

    forM_ benchmarks $ \benchmark -> do
      benchmarkDownloadRules benchmark

    "output/report.csv" %> \out -> do
      let stats = [ "output" </> benchmarkId b </> t </> "stats.csv"
                  | b <- benchmarks, t <- targets ]
      need stats
      case stats of
        s:rest -> do
          copyFile' s out
          forM_ rest $ \r -> do
            x:lines <- readFileLines r
            liftIO $ appendFile out (unlines lines)
        [] -> error "What"
    "output/all.csv" %> \out -> do
      let stats = [ "output" </> benchmarkId b </> t </> "stats.csv"
                  | b <- benchmarks, t <- all ]
      need stats
      case stats of
        s:rest -> do
          copyFile' s out
          forM_ rest $ \r -> do
            x:lines <- readFileLines r
            liftIO $ appendFile out (unlines lines)
        [] -> error "What"

    "output/*/initial/app.jar" %> \out -> do
      let
        extracted = takeDirectory out
        benchmark = takeDirectory extracted </> "benchmark"
      need [ benchmark </> "TIMESTAMP"
           , "scripts/benchmark.py"
           , "data/excluded-tests.txt"]
      cmd "scripts/benchmark.py" ["data/excluded-tests.txt", benchmark, extracted]

    "output//*/test.txt" %> \out -> do
      let from = takeDirectory out
      need [ from </> "app.jar", "scripts/run-test.sh"]
      x <- liftIO $ makeAbsolute from
      s <- liftIO $ makeAbsolute "scripts/run-test.sh"
      withTempDir $ \folder -> do
        Exit _ <- cmd (Cwd folder) (FileStdout out) (FileStderr out) [s] [ x ]
        return ()

    "output//*/stats.csv" %> \out -> do
      let from = takeDirectory out
      need [ from </> "test.txt", "scripts/metric.py"]
      cmd_ (FileStdout out) "scripts/metric.py" [from]

    "output//*+jreduce/app.jar" %> runScriptAction "scripts/run-jreduce.sh"
    "output//*+inliner/app.jar"  %> runScriptAction "scripts/run-inliner.sh"
    "output//*+jshrink/app.jar" %> runScriptAction "scripts/jshrink_script.sh"

runScriptAction :: FilePath -> FilePath -> Action ()
runScriptAction script out = do
  let
    outfolder = takeDirectory out
    from = List.init $ List.dropWhileEnd (/= '+') outfolder
  liftIO $ removeFiles outfolder ["//"]
  need [ from </> "app.jar"
        , "scripts/unjar.py"
        , script ]
  cmd_ script [from, outfolder]

benchmarkDownloadRules :: BenchmarkDesc -> Rules ()
benchmarkDownloadRules BenchmarkDesc {..} = do
  let benchmark = "output" </> benchmarkId </> "benchmark"

  benchmark </> ".git/HEAD" %> \out -> do
    liftIO $ removeFiles benchmark ["//"]
    cmd_ "git clone" [benchmarkUrl] [benchmark]
    cmd_ (Cwd benchmark) "git checkout -b onr" [benchmarkCommit]

  benchmark </> "TIMESTAMP" %> \out -> do
    need [benchmark </> ".git/HEAD", "scripts/run-test.sh"]
    let patchfile = "data/patches" </> benchmarkId <.> "patch"
    b <- doesFileExist patchfile
    if b
      then do
      need [patchfile]
      cmd_ (Cwd benchmark) "git apply" ["../../.." </> patchfile]
      else return ()
    writeFile' out ""

data BenchmarkDesc = BenchmarkDesc
  { benchmarkId :: String
  , benchmarkUrl :: String
  , benchmarkCommit :: String
  }

instance  FromRecord BenchmarkDesc where
  parseRecord v =
    BenchmarkDesc <$> v .! 0 <*> v .! 1 <*> v .! 2
