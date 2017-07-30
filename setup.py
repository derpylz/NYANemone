#!python

from distutils.core import setup

setup(name='nyanemone-win64',
      version='1.0',
      description='Workflow for tracking anemone larvae',
      author='Nils Jonathan Trost',
      author_email='nils.trost@stud.uni-heidelberg.de',
      packages=['nyanemone', 'nyanemone.external', 'nyanemone.tracking'],
      package_data={'nyanemone.external': ['data/*.txt']},
      scripts=['nyanemone/scripts/nyanemone_larva.py'])
