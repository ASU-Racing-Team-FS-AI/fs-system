from setuptools import find_packages, setup

package_name = "planning_centerline_calc"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="mohd_yasser1",
    maintainer_email="mohdyasser100@gmail.com",
    description="TODO: Package description",
    license="TODO: License declaration",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": ["my_script = planning_centerline_calc.node:main"],
    },
)