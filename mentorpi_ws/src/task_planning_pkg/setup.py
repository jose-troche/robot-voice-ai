from setuptools import setup

package_name = "task_planning_pkg"

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
    description="Task planning and agent-facing orchestration for voice-driven robot behavior.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "task_planner_node = task_planning_pkg.task_planner_node:main",
        ],
    },
)
