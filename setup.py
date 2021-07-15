import setuptools


setuptools.setup(

	name="ntm_profiler",

	version="0.0.1",
	packages=["ntm_profiler"],
	license="GPLv3",
	long_description="NTM-Profiler command line tool",
	scripts= [
		'scripts/ntm-profiler'
		],
	data_files=[('share/ntm_profiler',["db/ntm_db.kmers.txt"])]
)
