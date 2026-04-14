from setuptools import setup

package_name = "navigation_executor_pkg"

setup(
    name=package_name,
    version="0.0.1",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Robot Voice AI",
    maintainer_email="user@example.com",
    description="Semantic goal execution and future Nav2 action integration.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "navigation_executor_node = navigation_executor_pkg.navigation_executor_node:main",
        ],
    },
)
