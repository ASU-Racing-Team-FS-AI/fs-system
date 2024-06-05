# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_common_params_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED common_params_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(common_params_FOUND FALSE)
  elseif(NOT common_params_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(common_params_FOUND FALSE)
  endif()
  return()
endif()
set(_common_params_CONFIG_INCLUDED TRUE)

# output package information
if(NOT common_params_FIND_QUIETLY)
  message(STATUS "Found common_params: 2.0.0 (${common_params_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'common_params' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT ${common_params_DEPRECATED_QUIET})
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(common_params_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "")
foreach(_extra ${_extras})
  include("${common_params_DIR}/${_extra}")
endforeach()
