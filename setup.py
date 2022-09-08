from setuptools import setup, find_packages

requirements = open('./requirements.txt', 'r').read().split("\n")
print(requirements)
setup(
    name='falcon-utils',
    packages=['falcon_utils', 'falcon_utils.middlewares', 'falcon_utils.errors', 'falcon_utils.csv'],
    version='0.0.3',
    author="Develper Junio",
    author_email='developer@junio.in',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
    description="Falcon Utilities, Middlewares, Error Classes",
    license="MIT license",
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements)