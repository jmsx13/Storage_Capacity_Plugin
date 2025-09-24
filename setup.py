from setuptools import setup, find_packages

__author__ = 'Jaime Cevallos Sierra'
__copyright__ = "Copyright 2022, IN+ - Instituto Superior Técnico"
__credits__ = ["IN+ - Instituto Superior Técnico/Jaime Cevallos Sierra"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Jaime Cevallos Sierra"
__email__ = "jaime.cevallos@tecnico.ulisboa.pt / jmsx13@gmail.com"
__status__ = "Production"

setup(name='cea_storage_capacity',
      version=__version__,
      description="A storage capacity plugin for City Energy Analyst",
      license='MIT',
      author='Jaime Cevallos Sierra',
      author_email='jaime.cevallos@tecnico.ulisboa.pt / jmsx13@gmail.com',
      url='',
      long_description="A plugin for the City Energy Analyst to evaluate the storage benefits of a building",
      py_modules=[''],
      packages=find_packages(),
      package_data={},
      include_package_data=True)
