# Algae

A platform for running code plagiarism (cheating) detection software on large datasets.

## Using Algae

1. Clone the algae repo.
2. Set up a corpus. See the section below.
3. Make sure that clang and libclang are installed (along with python binding) (sudo apt-get install clang libclang-dev && sudo pip install clang). Many built-in processors require this.
4. Set up your detectors and configuration file.
5. View your results in the results viewer.

Then, run algae as follows from your algae folder:

```
python algae.py [mode] [jobs] [options]
```

If you see errors regarding libclang, head over to preprocessors/tokenizer/tokenizer.py and change the hardcoded path to point to the folder containing 'libclang.so'.

### Mode
- “all” - default if none specified - Runs the preprocessors, processor, and postprocessors in order.
- “preprocess|process|process+post|postprocess” - Runs only the specified lifecycle event. Using these automatically applies the ‘-force’ option.

### Jobs
- none specified - Runs all jobs from configuration
- one or more job names specified - Runs all jobs found in the configuration.

### Options
- --force - If present, ignores progress.json and will re-run all job steps.
Typically only used with mode ‘all’
- --config [filename] - Will use [filename] as the config instead of config.json.
- --clean - Will PERMANENTLY delete all data from ALL __algae__ folders in the corpus, then run with --force.

## Algae Folder Layout

- preprocessors
	- Your iles related to each preprocessor go here.
	- Each preprocessor can be comprised of any number of files or subfolders, and must have a unique Python entry point here.
- processors
	- Your files related to each processor go here
	- Each processor can be comprised of any number of files or subfolders, and must have a unique Python entry point here.
- postprocessors
	- Your files related to each postprocessor go here.
	- Each postprocessor can be comprised of any number of files or subfolders, and must have a unique Python entry point here.
- helpers
	- Algae submodules. Do not modify.
	- However, common.py does contain many potentially useful functions for your processors. Take a look, and feel free to use!
- algae.py (the main program)
- config.json (the Algae configuration file)
- progress_*.json (these will be automatically created)

## Corpus Folder Layout
The corpus is the set of students/assignment you want to run cheating detection on. It is also where Algae will store its results.

- path/to/corpus
	- [student 1 id]
		- [assignment 1 id]
			- Code files and folders go here.
			- \_\_algae\_\_ (folder will be automatically created)
				- Preprocessor output goes here.
		- ... (more assignments)
	- ... (more students)
	- \_\_algae\_\_ (folder will be automatically created)
		- processed
			- [assignment 1 id]
				- Processor results go here.
		- postprocessed
			- [assignment 1 id]
				- Postprocessor results go here.
	- students.txt (a list of student ids, one per line)
	- semesters.csv
		- Optional, but potentially useful.
		- "[studentId],[semesterId]" on each line
		- helpers.getSemester(student) API for processors.

## Configuration File
The configuration file (config.json) is the main driver of algae. It should be formatted as follows:

- root (object)
	- corpusPath (string): Path to the corpus
	- jobs (array):
		- For each (object):
			- name (string): The name of the job
			- assignments (array):
				- For each (object):
					- name (string): assignmentId
					- args (object - optional): args for this assignment
			- preprocessors (array - can be empty):
				- For each (object):
					- Either:
						- name (string): Name of the preprocessor to use (should correspond to name of entry point python file)
						- args (object - optional): Args that will be passed into the preprocessor.
					- Or:
						- job (string): Name of another job.
						- name (string): The name of the preprocessor from that job we should run (if it hasn’t already)
			- processor (object - required):
				- name (string): Same as above.
				- args (object - optional): Same as above.
			- postprocessors (array - can be empty):
				- For each (object):
					- name (string): Same as above.
					- args (object - optional): Same as above.

See the config.json provided for an example.

## Progress File
This file (progress_*.json, on per config file used) will be automatically created/managed and is used to ensure that processors (which can take on the order of days to run in some cases) only run if they haven't already. This way, one can adjust the parameters of a postprocessor and run Algae again without also having to rerun the processor. Using the --force option will override this.

## Processor API
Algae is designed to be extended with new processors.

A preprocessor/processor/postprocessor is a python program containing a function named “run” (and stored in the proper folder) that takes the following arguments:

- students - an array of all student ids
- assignments - the array of assignment that this processor should check
- args - args to the preprocessor/processor/postprocessor (passed in from config)
- helpers - a set of handy helper functions over the corpus (see implementation in helpers/corpus.py)

Processors should return True on success and False on failure.

## Viewing Results
Algae has a built-in results viewer. Simply run the following command from within your Algae folder:

```
python results.py
```

Note that you will need node installed for this to work.

## FERPA and Warnings

Do not run the results viewer on a computer than can be remotely accessed over HTTP by the general public:

- Student data (in the United States) is protected by a law called FERPA, and making this data publicly available (on purpose or not) constitutes a violation of this law.
- While the results viewer is running, an attacker can remotely access ANY file on your computer.

The more you know *tink*.
