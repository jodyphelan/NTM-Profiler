import setuptools

version = [l.strip() for l in open("ntm_profiler/__init__.py") if "version" in l][0].split('"')[1]

setuptools.setup(

	name="ntm_profiler",

	version=version,
	packages=["ntm_profiler"],
	license="GPLv3",
	long_description="NTM-Profiler command line tool",
	scripts= [
		'scripts/ntm-profiler'
		],
	# data_files=[('share/ntm_profiler',["db/ntm_db.kmers.txt"])]
)
