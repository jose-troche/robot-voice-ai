cmake_minimum_required(VERSION 3.10)
project(robot_voice_ai_interfaces)

# ROS Humble still pulls in FindPythonInterp/FindPythonLibs via
# python_cmake_module. Keep the legacy behavior enabled on newer CMake so the
# upstream module works without emitting CMP0148 developer warnings.
if(POLICY CMP0148)
  cmake_policy(SET CMP0148 OLD)
endif()

# `colcon` may pass this legacy catkin flag to CMake packages in mixed ROS
# environments. We do not need special handling for it here, but touching it
# marks the cache entry as used and avoids an otherwise noisy configure warning.
if(DEFINED CATKIN_INSTALL_INTO_PREFIX_ROOT)
  set(CATKIN_INSTALL_INTO_PREFIX_ROOT "${CATKIN_INSTALL_INTO_PREFIX_ROOT}")
endif()

# `colcon build --symlink-install` also forwards this catkin-era variable to
# plain CMake packages. Consume it as a no-op so CMake does not warn.
if(DEFINED CATKIN_SYMLINK_INSTALL)
  set(CATKIN_SYMLINK_INSTALL "${CATKIN_SYMLINK_INSTALL}")
endif()

# On macOS, the generated rosidl Python extension modules are installed under
# `lib/python*/site-packages/...` while the companion dylibs live in `lib/`.
# Teach CMake the final runtime search paths up front so it does not generate
# install-time `install_name_tool -delete_rpath` calls for build-only paths that
# newer Apple toolchains may already have omitted.
if(APPLE)
  set(CMAKE_BUILD_WITH_INSTALL_RPATH TRUE)
  set(CMAKE_INSTALL_RPATH "@loader_path;@loader_path/../../..")

  if(DEFINED ENV{CONDA_PREFIX})
    list(APPEND CMAKE_INSTALL_RPATH "$ENV{CONDA_PREFIX}/lib")
  endif()
endif()

# ROS Humble's Python discovery can get confused by Pixi/Conda on macOS and
# accidentally probe a different system Python. Seed the active environment's
# Python paths so rosidl_generator_py stays on the interpreter from `pixi run`.
if(APPLE AND DEFINED ENV{CONDA_PREFIX})
  set(_python_prefix "$ENV{CONDA_PREFIX}")
  set(_python_executable "${_python_prefix}/bin/python")

  if(EXISTS "${_python_executable}")
    execute_process(
      COMMAND "${_python_executable}" -c "import sysconfig; print(sysconfig.get_path('include')); print(sysconfig.get_config_var('LDLIBRARY') or ''); print(f'{sysconfig.get_config_var(\"py_version_short\") or \"\"}')"
      OUTPUT_VARIABLE _python_env_info
      RESULT_VARIABLE _python_env_result
      OUTPUT_STRIP_TRAILING_WHITESPACE
    )

    if(_python_env_result EQUAL 0)
      string(REPLACE "\n" ";" _python_env_info "${_python_env_info}")
      list(GET _python_env_info 0 _python_include_dir)
      list(GET _python_env_info 1 _python_library_name)
      list(GET _python_env_info 2 _python_version_short)
      set(_python_library "${_python_prefix}/lib/${_python_library_name}")

      if(NOT EXISTS "${_python_library}" AND NOT _python_version_short STREQUAL "")
        set(_python_library "${_python_prefix}/lib/libpython${_python_version_short}.dylib")
      endif()

      if(EXISTS "${_python_include_dir}" AND EXISTS "${_python_library}")
        execute_process(
          COMMAND "${_python_executable}" -c "import numpy; print(numpy.get_include())"
          OUTPUT_VARIABLE _python_numpy_include
          RESULT_VARIABLE _python_numpy_result
          OUTPUT_STRIP_TRAILING_WHITESPACE
        )

        set(Python_ROOT_DIR "${_python_prefix}" CACHE PATH "Python root directory" FORCE)
        set(Python3_ROOT_DIR "${_python_prefix}" CACHE PATH "Python3 root directory" FORCE)
        set(Python_FIND_VIRTUALENV FIRST CACHE STRING "Prefer the active virtual environment" FORCE)
        set(Python3_FIND_VIRTUALENV FIRST CACHE STRING "Prefer the active virtual environment" FORCE)
        set(Python_EXECUTABLE "${_python_executable}" CACHE FILEPATH "Python executable" FORCE)
        set(PYTHON_EXECUTABLE "${_python_executable}" CACHE FILEPATH "Python executable" FORCE)
        set(Python_INCLUDE_DIR "${_python_include_dir}" CACHE PATH "Python include directory" FORCE)
        set(Python_INCLUDE_DIRS "${_python_include_dir}" CACHE STRING "Python include directories" FORCE)
        set(PYTHON_INCLUDE_DIRS "${_python_include_dir}" CACHE STRING "Python include directories" FORCE)
        set(Python_LIBRARY "${_python_library}" CACHE FILEPATH "Python library" FORCE)
        set(Python_LIBRARIES "${_python_library}" CACHE STRING "Python libraries" FORCE)
        set(PYTHON_LIBRARY "${_python_library}" CACHE FILEPATH "Python library" FORCE)
        set(PYTHON_LIBRARIES "${_python_library}" CACHE STRING "Python libraries" FORCE)

        if(_python_numpy_result EQUAL 0 AND EXISTS "${_python_numpy_include}")
          set(Python_NumPy_INCLUDE_DIRS "${_python_numpy_include}" CACHE STRING "NumPy include directories" FORCE)
        endif()
      endif()
    endif()
  endif()
endif()

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(geometry_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/IntentCommand.msg"
  "msg/Room.msg"
  "msg/ObjectSighting.msg"
  "msg/TaskPlan.msg"
  "srv/GetRoom.srv"
  "srv/QueryObject.srv"
  DEPENDENCIES builtin_interfaces geometry_msgs
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
