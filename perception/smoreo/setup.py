from setuptools import find_packages, setup
import os
package_name = 'smoreo'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), ['launch/smoreo.launch.xml','launch/smoreo_tuner.launch.xml']) ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='farida',
    maintainer_email='farida@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [ 
            "smoreo= smoreo.smoreo_system:main"
        ],
    },
)