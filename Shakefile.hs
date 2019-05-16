{-# LANGUAGE RecordWildCards #-}
import Development.Shake
import Development.Shake.Command
import Development.Shake.FilePath
import Development.Shake.Util

import qualified Data.List as List

import System.Directory (makeAbsolute)

main :: IO ()
main = shakeArgs shakeOptions{shakeFiles="output"} $ do
    want ["output/01/report.txt", "output/00/report.txt"]

    phony "clean" $ do
        putNormal "Cleaning files in _build"
        removeFilesAfter "output" ["//*"]

    benchmarkDownloadRules
      (BenchmarkDesc
       "00"
       "https://github.com/apache/commons-lang"
       "3609993fb588017c77fc1781d697dcf1717cd73a")

    benchmarkDownloadRules
      (BenchmarkDesc
       "01"
       "https://github.com/aragozin/jvm-tools"
       "65ab61f56694426247ab62bb27e13c17de8c5953")

    "output/*/report.txt" %> \out -> do
      need [takeDirectory out </> "benchmark/TIMESTAMP"]
      writeFile' out ""

    "output/*/extracted/app.jar" %> \out -> do
      let
        extracted = takeDirectory out
        benchmark = takeDirectory extracted </> "benchmark"
      need [ benchmark </> "TIMESTAMP"
           , "scripts/benchmark.py"
           , "data/excluded-tests.txt"]
      cmd_ "scripts/benchmark.py" ["data/excluded-tests.txt", benchmark, extracted]

    "output//*/test.txt" %> \out -> do
      let from = takeDirectory out
      need [ from </> "app.jar", "scripts/run-test.sh"]
      x <- liftIO $ makeAbsolute from
      s <- liftIO $ makeAbsolute "scripts/run-test.sh"
      withTempDir $ \folder ->
        cmd_ (Cwd folder) (FileStdout out) (FileStderr out) [s] [ x ]

    "output//*/stats.csv" %> \out -> do
      let from = takeDirectory out
      need [ from </> "test.txt", "scripts/metric.py"]
      cmd_ (FileStdout out) "scripts/metric.py" [from]

    "output//*+jreduce/app.jar" %> \out -> do
      let
        outfolder = takeDirectory out
        from = List.init $ List.dropWhileEnd (/= '+') outfolder
      liftIO $ removeFiles outfolder ["//"]
      need [ from </> "app.jar"
           , "scripts/unjar.py"
           , "scripts/run-jreduce.sh"]
      cmd_ "scripts/run-jreduce.sh" [from, outfolder]

data BenchmarkDesc = BenchmarkDesc
  { benchmarkId :: String
  , benchmarkUrl :: String
  , benchmarkCommit :: String
  }

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
