"""
Flask-Logging-Extras
-------------------

Flask-Logging-Extras provides extra logging functionality for Flask apps.
"""

from setuptools import setup

setup(name='Flask-Logging-Extras',
      version='0.1.1',
      url='https://github.com/gergelypolonkai/flask-logging-extras',
      license='MIT',
      author='Gergely Polonkai',
      author_email='gergely@polonkai.eu',
      description='Extra logging functionality for Flask apps',
      long_description='Extra logging functionality for Flask apps.',
      keywords = ['flask', 'logging'],
      packages=['flask_logging_extras'],
      zip_safe=False,
      platforms='any',
      install_requires=['Flask'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
      ])
