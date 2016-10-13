# AnalysisToolLight

Below is a description of the structure of this repo:
- **AnalysisTool**
   - **batch**: directory for batch work: jobs can be submitted from here. output goes in results directory of main repo (AnalysisToolLight/results/)
      - **results**: results of batch jobs go in here
      - `batch.sh`: batch job script, eg. used in bsub command
   - **data** ||| input for jobs: input file lists, scale factors, etc.
      - **pileup**: contains rootfiles output by the pileup scripts in the scripts directory
   - **python**
      - **batch**: misc. tools for batch submission
         - `batch_helper.py`
         - `datasets.py`
      - **tools**: misc. tools for analyser
         - `tools.py`
      - `AnalysisBase.py`: defines base class used for analysis. sets up analysis job for the derived class but does no analysis itself.
      - `Dataform.py`: defines objects used by AnalysisBase class: events, muons, jets, etc.
   - **scripts**
      - `getDataPileupDist.sh`: creates a root file with the data pileup histogram, given a JSON and min bias cross section. The root file is then used by generatePileupDist.py
      - `generatePileupDist.py`: generates a root file with scale factors for MC, given the CMSSW version that the original miniAODs were created from and the root files output by getDataPileupDist.sh. This creates AnalysisTool/data/pileup/pileup_76X.root
   - **templates**
      - `FinalState_2mu_template.py`: template analysis with examples of how to access all objects and some methods
   - **VH**: directory for analysis of VH channel
      - **python**: code for each final state (in VH) to be analysed goes here
         - `FinalState_4mu.py`: analysis code for VH->4muon final state
   - `run_local.sh`: example of how to run an analysis job locally

