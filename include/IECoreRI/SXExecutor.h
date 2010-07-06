//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2010, Image Engine Design Inc. All rights reserved.
//
//  Redistribution and use in source and binary forms, with or without
//  modification, are permitted provided that the following conditions are
//  met:
//
//     * Redistributions of source code must retain the above copyright
//       notice, this list of conditions and the following disclaimer.
//
//     * Redistributions in binary form must reproduce the above copyright
//       notice, this list of conditions and the following disclaimer in the
//       documentation and/or other materials provided with the distribution.
//
//     * Neither the name of Image Engine Design nor the names of any
//       other contributors to this software may be used to endorse or
//       promote products derived from this software without specific prior
//       written permission.
//
//  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
//  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
//  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
//  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
//  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
//  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
//  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
//  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
//  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
//  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
//  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//
//////////////////////////////////////////////////////////////////////////

#ifndef IECORERI_SXEXECUTOR_H
#define IECORERI_SXEXECUTOR_H

#include "boost/noncopyable.hpp"

#include "OpenEXR/ImathVec.h"

#include "sx.h"

#include "IECore/CompoundData.h"

namespace IECoreRI
{

/// This class simplifies the execution of shaders using the Sx library by
/// wrapping it to accept IECore datatypes for input and output.
class SXExecutor : public boost::noncopyable
{

	public :
	
		typedef std::vector<SxShader> ShaderVector;
	
		/// Constructs an executor for the specified set of shaders, coshaders and lights.
		/// The shaders in the shaders parameter will be run in sequence, with the output from
		/// one forming the input to the next. It is the caller's responsibility to ensure that the ShaderVectors
		/// remain alive for as long as the executor is in use.
		SXExecutor( const ShaderVector *shaders, const ShaderVector *coshaders = 0, const ShaderVector *lights = 0 );

		/// Executes the shader for the specified points. The points are considered
		/// to have no specific connectivity, meaning that area and filtering functions
		/// will be effectively disabled during shader execution.
		IECore::CompoundDataPtr execute( const IECore::CompoundData *points ) const;
		/// Executes the shader for the specified points. The points are considered to
		/// have a grid topology of the specified dimensions in u and v space, and this
		/// topology will be used to implement proper filtering and area functions. u, v, du and dv
		/// shading variables will be automatically calculated if not provided but they may also
		/// be passed explicitly if desired. If gridSize is <=0 in either dimension then this method
		/// is equivalent to the method above, and no topology is assumed.
		IECore::CompoundDataPtr execute( const IECore::CompoundData *points, const Imath::V2i &gridSize ) const;

	private :

		SxType predefinedParameterType( const char *name ) const;
		
		void setVariables( SxParameterList parameterList, SxShader targetShader, SxShader previousShader, const IECore::CompoundData *points, size_t expectedSize ) const;
		
		void setVariable( SxParameterList parameterList, const char *name, SxType type, bool predefined, SxShader previousShader, const IECore::CompoundData *points, size_t expectedSize ) const;
		template<SxType>
		void setVariable2( SxParameterList parameterList, const char *name, bool predefined, SxShader previousShader, const IECore::CompoundData *points, size_t expectedSize ) const;
		
		template<typename T>
		void getVariable( SxShader shader, const char *name, IECore::CompoundData *container ) const;

		const ShaderVector *m_shaders;
		const ShaderVector *m_coshaders;
		const ShaderVector *m_lights;

};

} // namespace IECoreRI

#endif // IECORERI_SXEXECUTOR_H
