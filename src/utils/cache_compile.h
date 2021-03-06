// ***************************************************************
// Copyright (c) 2020 Jittor. Authors: Dun Liang <randonlang@gmail.com>. All Rights Reserved.
// This file is subject to the terms and conditions defined in
// file 'LICENSE.txt', which is part of this source code package.
// ***************************************************************
#pragma once
#include "common.h"

namespace jittor {
namespace jit_compiler {

string read_all(const string& fname);
void write(const string& fname, const string& src);
bool file_exist(const string& fname);
string join(string a, string b);
bool cache_compile(const string& cmd, const string& cache_path="", const string& jittor_path="");

} // jit_compiler
} // jittor