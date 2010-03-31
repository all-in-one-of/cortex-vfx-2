##########################################################################
#
#  Copyright (c) 2007-2010, Image Engine Design Inc. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#     * Neither the name of Image Engine Design nor the names of any
#       other contributors to this software may be used to endorse or
#       promote products derived from this software without specific prior
#       written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##########################################################################

from __future__ import with_statement

import unittest
import os
import os.path
import threading
import math

from IECore import *

from IECoreGL import *
init( False )

class TestRenderer( unittest.TestCase ) :

	def testOptions( self ) :

		os.environ["IECOREGL_TEXTURE_PATHS"] = "textureDefault"
		os.environ["IECOREGL_SHADER_PATHS"] = "shaderDefault"

		r = Renderer()

		self.assertEqual( r.typeName(), "IECoreGL::Renderer" )

		self.assertEqual( r.getOption( "searchPath:texture" ), StringData( "textureDefault" ) )
		self.assertEqual( r.getOption( "gl:searchPath:texture" ), StringData( "textureDefault" ) )

		r.setOption( "searchPath:texture", StringData( "a" ) )
		self.assertEqual( r.getOption( "searchPath:texture" ), StringData( "a" ) )
		self.assertEqual( r.getOption( "gl:searchPath:texture" ), StringData( "a" ) )

		r.setOption( "gl:searchPath:texture", StringData( "b" ) )
		self.assertEqual( r.getOption( "searchPath:texture" ), StringData( "b" ) )
		self.assertEqual( r.getOption( "gl:searchPath:texture" ), StringData( "b" ) )

		self.assertEqual( r.getOption( "searchPath:shader" ), StringData( "shaderDefault" ) )
		self.assertEqual( r.getOption( "gl:searchPath:shader" ), StringData( "shaderDefault" ) )

		r.setOption( "searchPath:shader", StringData( "s" ) )
		self.assertEqual( r.getOption( "searchPath:shader" ), StringData( "s" ) )
		self.assertEqual( r.getOption( "gl:searchPath:shader" ), StringData( "s" ) )

		r.setOption( "gl:searchPath:shader", StringData( "t" ) )
		self.assertEqual( r.getOption( "searchPath:shader" ), StringData( "t" ) )
		self.assertEqual( r.getOption( "gl:searchPath:shader" ), StringData( "t" ) )

		self.assertEqual( r.getOption( "shutter" ), V2fData( V2f( 0 ) ) )
		r.setOption( "shutter", V2fData( V2f( 1, 2 ) ) )
		self.assertEqual( r.getOption( "shutter" ), V2fData( V2f( 1, 2 ) ) )

	def testAttributes( self ) :

		deferred = Renderer()
		deferred.setOption( "gl:mode", StringData( "deferred" ) )

		immediate = Renderer()
		immediate.setOption( "gl:mode", StringData( "immediate" ) )


		for r in [ deferred, immediate ] :

			r.worldBegin()

			self.assertEqual( r.getAttribute( "color" ), Color3fData( Color3f( 1 ) ) )
			self.assertEqual( r.getAttribute( "opacity" ), Color3fData( Color3f( 1 ) ) )
			self.assertEqual( r.getAttribute( "gl:color" ), Color4fData( Color4f( 1 ) ) )
			self.assertEqual( r.getAttribute( "gl:blend:color" ), Color4fData( Color4f( 1 ) ) )
			self.assertEqual( r.getAttribute( "gl:blend:srcFactor" ), StringData( "srcAlpha" ) )
			self.assertEqual( r.getAttribute( "gl:blend:dstFactor" ), StringData( "oneMinusSrcAlpha" ) )
			self.assertEqual( r.getAttribute( "gl:blend:equation" ), StringData( "add" ) )
			self.assertEqual( r.getAttribute( "gl:shade:transparent" ), BoolData( False ) )
			self.assertEqual( r.getAttribute( "gl:primitive:sortForTransparency" ), BoolData( True ) )
			self.assertEqual( r.getAttribute( "name" ), StringData( "unnamed" ) )
			self.assertEqual( r.getAttribute( "doubleSided" ), BoolData( True ) )
			self.assertEqual( r.getAttribute( "gl:smoothing:points" ), BoolData( False ) )
			self.assertEqual( r.getAttribute( "gl:smoothing:lines" ), BoolData( False ) )
			self.assertEqual( r.getAttribute( "gl:smoothing:polygons" ), BoolData( False ) )
			if withFreeType() :
				self.assertEqual( r.getAttribute( "gl:textPrimitive:type" ), StringData( "mesh" ) )

			r.setAttribute( "color", Color3fData( Color3f( 0, 1, 2 ) ) )
			self.assertEqual( r.getAttribute( "color" ), Color3fData( Color3f( 0, 1, 2 ) ) )

			# opacity is an odd one - it's set as a color but as it's averaged internally
			# the result you get should be a greyscale value.
			r.setAttribute( "opacity", Color3fData( Color3f( 3, 1, 2 ) ) )
			self.assertEqual( r.getAttribute( "opacity" ), Color3fData( Color3f( 2 ) ) )

			self.assertEqual( r.getAttribute( "gl:color" ), Color4fData( Color4f( 0, 1, 2, 2 ) ) )
			r.setAttribute( "gl:color", Color4fData( Color4f( 1, 2, 3, 4 ) ) )
			self.assertEqual( r.getAttribute( "gl:color" ), Color4fData( Color4f( 1, 2, 3, 4 ) ) )

			r.setAttribute( "gl:blend:color", Color4fData( Color4f( 0, 1, 0, 1 ) ) )
			self.assertEqual( r.getAttribute( "gl:blend:color" ), Color4fData( Color4f( 0, 1, 0, 1 ) ) )

			r.attributeBegin()
			r.setAttribute( "color", Color3fData( Color3f( 0 ) ) )
			self.assertEqual( r.getAttribute( "gl:color" ), Color4fData( Color4f( 0, 0, 0, 4 ) ) )
			r.attributeEnd()
			self.assertEqual( r.getAttribute( "gl:color" ), Color4fData( Color4f( 1, 2, 3, 4 ) ) )

			factors = [ "zero", "one", "srcColor", "oneMinusSrcColor", "dstColor", "oneMinusDstColor",
				"srcAlpha", "oneMinusSrcAlpha", "dstAlpha", "oneMinusDstAlpha", "dstAlpha", "oneMinusDstAlpha",
				"constantColor", "oneMinusConstantColor", "constantAlpha", "oneMinusConstantAlpha" ]
			for f in factors :
				last = r.getAttribute( "gl:blend:dstFactor" )
				r.setAttribute( "gl:blend:srcFactor", StringData( f ) )
				self.assertEqual( r.getAttribute( "gl:blend:srcFactor" ), StringData( f ) )
				self.assertEqual( r.getAttribute( "gl:blend:dstFactor" ), last )
				last = r.getAttribute( "gl:blend:srcFactor" )
				r.setAttribute( "gl:blend:dstFactor", StringData( f ) )
				self.assertEqual( r.getAttribute( "gl:blend:srcFactor" ), StringData( f ) )
				self.assertEqual( r.getAttribute( "gl:blend:dstFactor" ), last )

			for e in ["add", "subtract", "reverseSubtract", "min", "max"] :
				r.setAttribute( "gl:blend:equation", StringData( e ) )
				self.assertEqual( r.getAttribute( "gl:blend:equation" ), StringData( e ) )

			r.setAttribute( "name", StringData( "sphere" ) )
			self.assertEqual( r.getAttribute( "name" ), StringData( "sphere" ) )

			r.setAttribute( "doubleSided", BoolData( False ) )
			self.assertEqual( r.getAttribute( "doubleSided" ), BoolData( False ) )

			r.setAttribute( "gl:smoothing:points", BoolData( True ) )
			self.assertEqual( r.getAttribute( "gl:smoothing:points" ), BoolData( True ) )
			r.setAttribute( "gl:smoothing:lines", BoolData( True ) )
			self.assertEqual( r.getAttribute( "gl:smoothing:lines" ), BoolData( True ) )
			r.setAttribute( "gl:smoothing:polygons", BoolData( True ) )
			self.assertEqual( r.getAttribute( "gl:smoothing:polygons" ), BoolData( True ) )

			if withFreeType() :
				r.setAttribute( "gl:textPrimitive:type", StringData( "sprite" ) )
				self.assertEqual( r.getAttribute( "gl:textPrimitive:type" ), StringData( "sprite" ) )

			r.worldEnd()

	def testOtherRendererAttributes( self ) :

		"""Attributes destined for other renderers should be silently ignored."""

		deferred = Renderer()
		deferred.setOption( "gl:mode", StringData( "deferred" ) )

		immediate = Renderer()
		immediate.setOption( "gl:mode", StringData( "immediate" ) )

		handler = CapturingMessageHandler()
		Msg.pushHandler( handler )

		for r in [ deferred, immediate ] :

			r.worldBegin()

			r.setAttribute( "ri:visibility:diffuse", IntData( 0 ) )

			r.worldEnd()

		Msg.popHandler()

		self.assertEqual( len( handler.messages ), 0 )

	## \todo Make this test assert something
	def testStacks( self ) :

		r = Renderer()
		r.setOption( "gl:mode", StringData( "deferred" ) )
		r.setOption( "gl:searchPath:shader", StringData( os.path.dirname( __file__ ) + "/shaders" ) )
		r.worldBegin()

		# we have to make this here so that the shaders that get made are made in the
		# correct GL context. My understanding is that all shaders should work in all
		# GL contexts in the address space, but that doesn't seem to be the case.
		#w = SceneViewer( "scene", r.scene() )

		r.concatTransform( M44f.createTranslated( V3f( 0, 0, -5 ) ) )
		r.shader( "surface", "color", { "colorValue" : Color3fData( Color3f( 1, 0, 0 ) ) } )
		r.geometry( "sphere", {}, {} )

		r.concatTransform( M44f.createTranslated( V3f( -1, 0, 0 ) ) )
		r.shader( "surface", "color", { "colorValue" : Color3fData( Color3f( 0, 1, 0 ) ) } )
		r.geometry( "sphere", {}, {} )

		r.concatTransform( M44f.createTranslated( V3f( 2, 0, 0 ) ) )
		r.shader( "surface", "color", { "colorValue" : Color3fData( Color3f( 0, 0, 1 ) ) } )
		r.geometry( "sphere", {}, {} )

		r.worldEnd()

		#w.start()

	def testStackBug( self ) :

		# This should produce a yellow sphere in between two red spheres. It does in the DeferredRenderer but
		# currently fails in the ImmediateRenderer.

		r = Renderer()
		r.setOption( "gl:mode", StringData( "immediate" ) )
		r.setOption( "gl:searchPath:shader", StringData( os.path.dirname( __file__ ) + "/shaders" ) )
		r.display( os.path.dirname( __file__ ) + "/output/testStackBug.tif", "tiff", "rgba", {} )
		r.worldBegin()

		r.shader( "surface", "rgbColor", { "red" : FloatData( 1 ), "green" : FloatData( 0 ), "blue" : FloatData( 0 ) } )

		r.concatTransform( M44f.createTranslated( V3f( 0, 0, -5 ) ) )

		r.attributeBegin()

		r.shader( "surface", "rgbColor", { "red" : FloatData( 1 ), "green" : FloatData( 1 ), "blue" : FloatData( 0 ) } )
		r.geometry( "sphere", {}, {} )

		r.attributeEnd()

		r.concatTransform( M44f.createTranslated( V3f( -1, 0, 0 ) ) )
		r.geometry( "sphere", {}, {} )

		r.concatTransform( M44f.createTranslated( V3f( 2, 0, 0 ) ) )
		r.geometry( "sphere", {}, {} )

		r.worldEnd()

		i = Reader.create( os.path.dirname( __file__ ) + "/output/testStackBug.tif" ).read()
		e = PrimitiveEvaluator.create( i )
		result = e.createResult()
		r = e.R()
		g = e.G()
		b = e.B()

		e.pointAtUV( V2f( 0.5, 0.5 ), result )
		self.assertEqual( result.floatPrimVar( r ), 1 )
		self.assertEqual( result.floatPrimVar( g ), 1 )
		self.assertEqual( result.floatPrimVar( b ), 0 )
		e.pointAtUV( V2f( 0, 0.5 ), result )
		self.assertEqual( result.floatPrimVar( r ), 1 )
		self.assertEqual( result.floatPrimVar( g ), 0 )
		self.assertEqual( result.floatPrimVar( b ), 0 )
		e.pointAtUV( V2f( 1, 0.5 ), result )
		self.assertEqual( result.floatPrimVar( r ), 1 )
		self.assertEqual( result.floatPrimVar( g ), 0 )
		self.assertEqual( result.floatPrimVar( b ), 0 )

	def testPrimVars( self ) :

		r = Renderer()
		r.setOption( "gl:mode", StringData( "immediate" ) )
		r.setOption( "gl:searchPath:shader", StringData( os.path.dirname( __file__ ) + "/shaders" ) )
		r.display( os.path.dirname( __file__ ) + "/output/testPrimVars.tif", "tiff", "rgba", {} )
		r.worldBegin()

		r.shader( "surface", "rgbColor", {} )

		r.concatTransform( M44f.createTranslated( V3f( 0, 0, -5 ) ) )

		r.attributeBegin()

		# should make red, green and blue spheres
		r.geometry( "sphere", {}, {
				"red" : PrimitiveVariable( PrimitiveVariable.Interpolation.Constant, FloatData( 1 ) ),
				"green" : PrimitiveVariable( PrimitiveVariable.Interpolation.Constant, FloatData( 0 ) ),
				"blue" : PrimitiveVariable( PrimitiveVariable.Interpolation.Constant, FloatData( 0 ) ),
			}
		)

		r.attributeEnd()

		r.concatTransform( M44f.createTranslated( V3f( -1, 0, 0 ) ) )
		r.geometry( "sphere", {}, {
				"red" : PrimitiveVariable( PrimitiveVariable.Interpolation.Constant, FloatData( 0 ) ),
				"green" : PrimitiveVariable( PrimitiveVariable.Interpolation.Constant, FloatData( 1 ) ),
				"blue" : PrimitiveVariable( PrimitiveVariable.Interpolation.Constant, FloatData( 0 ) ),
			}
		)

		r.concatTransform( M44f.createTranslated( V3f( 2, 0, 0 ) ) )
		r.geometry( "sphere", {}, {
				"red" : PrimitiveVariable( PrimitiveVariable.Interpolation.Constant, FloatData( 0 ) ),
				"green" : PrimitiveVariable( PrimitiveVariable.Interpolation.Constant, FloatData( 0 ) ),
				"blue" : PrimitiveVariable( PrimitiveVariable.Interpolation.Constant, FloatData( 1 ) ),
			}
		)

		r.worldEnd()

		i = Reader.create( os.path.dirname( __file__ ) + "/output/testPrimVars.tif" ).read()
		e = PrimitiveEvaluator.create( i )
		result = e.createResult()
		r = e.R()
		g = e.G()
		b = e.B()

		e.pointAtUV( V2f( 0, 0.5 ), result )
		self.assertEqual( result.floatPrimVar( r ), 0 )
		self.assertEqual( result.floatPrimVar( g ), 1 )
		self.assertEqual( result.floatPrimVar( b ), 0 )
		e.pointAtUV( V2f( 0.5, 0.5 ), result )
		self.assertEqual( result.floatPrimVar( r ), 1 )
		self.assertEqual( result.floatPrimVar( g ), 0 )
		self.assertEqual( result.floatPrimVar( b ), 0 )
		e.pointAtUV( V2f( 1, 0.5 ), result )
		self.assertEqual( result.floatPrimVar( r ), 0 )
		self.assertEqual( result.floatPrimVar( g ), 0 )
		self.assertEqual( result.floatPrimVar( b ), 1 )

	## \todo Make this assert something
	def testImagePrimitive( self ) :

		r = Renderer()
		r.setOption( "gl:mode", StringData( "immediate" ) )
		r.setOption( "gl:searchPath:shader", StringData( os.path.dirname( __file__ ) + "/shaders" ) )
		r.display( os.path.dirname( __file__ ) + "/output/testImage.tif", "tiff", "rgba", {} )

		r.worldBegin()

		r.shader( "surface", "color", { "colorValue" : Color3fData( Color3f( 1, 0, 0 ) ) } )

		r.concatTransform( M44f.createTranslated( V3f( 0, 0, -5 ) ) )
		r.concatTransform( M44f.createScaled( V3f( 0.005 ) ) )

		i = Reader.create( os.path.dirname( __file__ ) + "/images/numbers.exr" ).read()
		i.render( r )

		r.worldEnd()

	## \todo Make this assert something
	def testAlphaBlending( self ) :

		r = Renderer()
		r.setOption( "gl:mode", StringData( "deferred" ) )
		r.setOption( "gl:searchPath:shader", StringData( os.path.dirname( __file__ ) + "/shaders" ) )

		r.worldBegin()
		#w = SceneViewer( "scene", r.scene() )

		r.setAttribute( "gl:blend:srcFactor", StringData( "one" ) )
		r.setAttribute( "gl:blend:dstFactor", StringData( "one" ) )
		r.setAttribute( "gl:blend:equation", StringData( "add" ) )

		r.concatTransform( M44f.createTranslated( V3f( 0, 0, -5 ) ) )
		r.concatTransform( M44f.createScaled( V3f( 0.004 ) ) )

		r.concatTransform( M44f.createTranslated( V3f( -150, -200, 0 ) ) )
		i = Reader.create( os.path.dirname( __file__ ) + "/images/numberWithAlpha.exr" ).read()
		i.render( r )

		r.concatTransform( M44f.createTranslated( V3f( 300, 300, 1 ) ) )
		i.render( r )

		r.worldEnd()

		#w.start()

	def testProcedural( self ) :

		r = Renderer()
		r.setOption( "gl:mode", StringData( "immediate" ) )
		r.setOption( "gl:searchPath:shader", StringData( os.path.dirname( __file__ ) + "/shaders" ) )
		r.display( os.path.dirname( __file__ ) + "/output/proceduralTest.tif", "tiff", "rgba", {} )

		r.worldBegin()

		r.shader( "surface", "color", { "colorValue" : Color3fData( Color3f( 1, 0, 0 ) ) } )

		r.concatTransform( M44f.createTranslated( V3f( 0, 0, -5 ) ) )
		r.concatTransform( M44f.createScaled( V3f( 0.1 ) ) )

		p = ReadProcedural()
		p["files"]["name"].setValue( StringData( "test/IECore/data/cobFiles/pSphereShape1.cob" ) )

		p.render( r )

		r.worldEnd()

		expectedImage = Reader.create( os.path.dirname( __file__ ) + "/expectedOutput/proceduralTest.tif" )()
		actualImage = Reader.create( os.path.dirname( __file__ ) + "/output/proceduralTest.tif" )()

		self.assertEqual( ImageDiffOp()( imageA = expectedImage, imageB = actualImage, maxError = 0.05 ).value, False )

	## \todo Make this assert something
	def testShader( self ) :

		r = Renderer()
		r.setOption( "gl:mode", StringData( "deferred" ) )
		r.setOption( "gl:searchPath:shader", StringData( os.path.dirname( __file__ ) + "/shaders" ) )
		r.setOption( "gl:searchPath:shaderInclude", StringData( os.path.dirname( __file__ ) + "/shaders/include" ) )

		r.worldBegin()
		r.shader( "surface", "color", { "colorValue" : Color3fData( Color3f( 1, 0, 0 ) ) } )
		r.concatTransform( M44f.createTranslated( V3f( 0, 0, -5 ) ) )
		r.geometry( "sphere", {}, {} )
		r.worldEnd()

		s = r.scene()

		s.render( State( True ) )
		
	def testRemoveObject( self ) :
	
		r = Renderer()
		r.setOption( "gl:mode", StringData( "deferred" ) )
		with WorldBlock( r ) :
		
			r.setAttribute( "name", "sphereOne" )
		
			r.sphere( 1, -1, 1, 360, {} )
			
			r.setAttribute( "name", "sphereTwo" )
		
			r.sphere( 1, -1, 1, 360, {} )

		s = r.scene()
		self.assertEqual( len( s.root().children() ), 2 )
		
		commandResult = r.command( "removeObject", { "name" : StringData( "sphereOne" ) } )
		self.assertEqual( commandResult, BoolData( True ) )
		self.assertEqual( len( s.root().children() ), 1 )

	def testParallelRenders( self ):

		allScenes = []
		
		def threadedRendering():
			r = Renderer()
			r.setOption( "gl:mode", StringData( "deferred" ) )
			r.setOption( "gl:searchPath:shader", StringData( os.path.dirname( __file__ ) + "/shaders" ) )
			r.setOption( "gl:searchPath:shaderInclude", StringData( os.path.dirname( __file__ ) + "/shaders/include" ) )

			r.worldBegin()
			r.shader( "surface", "failWithoutPreprocessing", {} )
			r.concatTransform( M44f.createTranslated( V3f( 0, 0, -5 ) ) )
			r.worldEnd()
			allScenes.append( r.scene() )

		for i in xrange( 0, 100 ):
			newThread = threading.Thread(target=threadedRendering)
			newThread.start()

		while len(allScenes) < 100 :
			pass

		for s in allScenes :
			s.render( State( True ) )

	class RecursiveProcedural( Renderer.Procedural ):
		"""Creates a pyramid of spheres"""

		maxLevel = 5
		threadsUsed = set()

		def __init__( self, level = 0 ):
			Renderer.Procedural.__init__( self )
			self.__level = level
			if level == 0 :
				self.threadsUsed.clear()

		def bound( self ) :
			return Box3f( V3f( -1 ), V3f( 1 ) )

		def render( self, renderer ):
			# registers this thread id
			self.threadsUsed.add( threading.current_thread().ident )
			renderer.attributeBegin()
			renderer.setAttribute( "color", Color3fData( Color3f( float(self.__level)/self.maxLevel, 0, 1 - float(self.__level)/self.maxLevel ) ) )
			renderer.transformBegin()
			renderer.concatTransform( M44f.createTranslated(V3f( 0, 0.5, 0 )) )
			renderer.concatTransform( M44f.createScaled( V3f(0.5) ) )
			renderer.geometry( "sphere", {}, {} )
			renderer.transformEnd()
			# end of recursion
			if self.__level < self.maxLevel :
				renderer.transformBegin()
				renderer.concatTransform( M44f.createTranslated(V3f( 0, -0.5, 0 )) )
				for i in xrange( 0, 2 ) :
					renderer.transformBegin()
					renderer.concatTransform( M44f.createTranslated(V3f( (i - 0.5) , 0, 0)) )
					renderer.concatTransform( M44f.createScaled( V3f(0.5) ) )
					proc = TestRenderer.RecursiveProcedural( self.__level + 1 )
					renderer.procedural( proc )
					renderer.transformEnd()
				renderer.transformEnd()
			renderer.attributeEnd()

	class RecursiveParameterisedProcedural( ParameterisedProcedural ):

		maxLevel = 5
		threadsUsed = set()

		def __init__( self, level = 0 ):
			ParameterisedProcedural.__init__( self )
			self.__level = level
			if level == 0 :
				self.threadsUsed.clear()

		def doRenderState( self, renderer, args ):
			pass

		def doBound( self, args ) :
			return Box3f( V3f( -1 ), V3f( 1 ) )

		def doRender( self, renderer, args ):
			# registers this thread id
			self.threadsUsed.add( threading.current_thread().ident )
			# end of recursion
			if self.__level < self.maxLevel :
				for i in xrange( 0, 2 ) :
					proc = TestRenderer.RecursiveParameterisedProcedural( self.__level + 1 )
					proc.render( renderer )

	def __testMultithreadedProcedural( self, procType ):

		r = Renderer()
		r.setOption( "gl:mode", StringData( "deferred" ) )
		r.setOption( "gl:searchPath:shader", StringData( os.path.dirname( __file__ ) + "/shaders" ) )
		r.setOption( "gl:searchPath:shaderInclude", StringData( os.path.dirname( __file__ ) + "/shaders/include" ) )
		r.worldBegin()
		p = procType()
		if isinstance( p, Renderer.Procedural ):
			r.procedural( p )
		else:
			p.render( r )
		r.worldEnd()

		self.assert_( len(procType.threadsUsed) > 1 )

	def __testParallelMultithreadedProcedurals( self, procType ):

		renders = []

		def newRender():
			r = Renderer()
			r.setOption( "gl:mode", StringData( "deferred" ) )
			r.setOption( "gl:searchPath:shader", StringData( os.path.dirname( __file__ ) + "/shaders" ) )
			r.setOption( "gl:searchPath:shaderInclude", StringData( os.path.dirname( __file__ ) + "/shaders/include" ) )
			r.worldBegin()
			p = procType()
			if isinstance( p, Renderer.Procedural ):
				r.procedural( p )
			else:
				p.render( r )
			r.worldEnd()
			renders.append( 0 )

		threads = []
		for i in xrange( 0,10 ):
			newThread = threading.Thread(target=newRender)
			newThread.start()
			threads.append( newThread )
		
		for t in threads :
			t.join()

	def testMultithreadedProcedural( self ):
		self.__testMultithreadedProcedural( self.RecursiveProcedural )

	def testMultithreadedParameterisedProcedural( self ):
		self.__testMultithreadedProcedural( self.RecursiveParameterisedProcedural )

	def testParallelMultithreadedProcedurals( self ):
		self.__testParallelMultithreadedProcedurals( self.RecursiveProcedural )

	def testParallelMultithreadedProcedurals( self ):
		self.__testParallelMultithreadedProcedurals( self.RecursiveParameterisedProcedural )

	def __countChildrenRecursive( self, g ) :
		if not isinstance( g, Group ):
			return 1
		count = 0
		for c in g.children():
			count += self.__countChildrenRecursive( c )
		return count

	def testObjectSpaceCulling( self ):

		p = self.RecursiveProcedural()

		def renderWithCulling( box ):
			r = Renderer()
			r.setOption( "gl:mode", StringData( "deferred" ) )
			r.worldBegin()
			r.sphere( 1.5, 0, 1, 360, {} )
			r.procedural( p )
			r.attributeBegin()
			if True:
				r.setAttribute( "gl:cullingSpace", StringData( "object" ) )
				r.setAttribute( "gl:cullingBox", Box3fData( box ) )
				# everything in this block is culled
				r.sphere( 1.5, 0, 1, 360, {} )
				r.procedural( p )
			r.attributeEnd()
			r.worldEnd()
			return self.__countChildrenRecursive( r.scene().root() )

		noCullingCounter = renderWithCulling( Box3f() )

		# verify that only half of the things are renderer when the giving culling box is defined.
		self.assertEqual( renderWithCulling( Box3f( V3f(2,-1,-1), V3f(3,1,1)  ) ) * 2, noCullingCounter )

	def testWorldSpaceCulling( self ):

		p = self.RecursiveProcedural()
		box = Box3f( V3f(0.001,-1,-1), V3f(1,1,1) )

		r = Renderer()
		r.setOption( "gl:mode", StringData( "deferred" ) )
		r.worldBegin()
		r.setAttribute( "gl:cullingSpace", StringData( "world" ) )
		r.setAttribute( "gl:cullingBox", Box3fData( box ) )
		r.sphere( 1, 0, 1, 360, {} )	# half-inside : 1 element
		r.procedural( p )	# half-inside: 32 elements (full procedural renders 63 elements)
		r.transformBegin()
		if True:
			r.concatTransform( M44f.createTranslated( V3f(-2, 0, 0) ) )
			# everything in this block is culled
			r.sphere( 1, 0, 1, 360, {} )
			r.procedural( p )
		r.transformEnd()
		r.worldEnd()
		self.assertEqual( self.__countChildrenRecursive( r.scene().root() ), 33 )

	def testTransformsInImmediateRenderer( self ):
		r = Renderer()
		r.setOption( "gl:mode", StringData( "immediate" ) )
		r.transformBegin()
		r.concatTransform( M44f.createRotated( V3f( 1, 1, 1 ) ) )
		r.camera( "main", { "resolution" : V2iData( V2i( 512 ) ), "projection" : StringData( "perspective" ) } )
		r.transformEnd()
		r.worldBegin()
		# confirm that the camera transformation is not affecting the world space matrix
		r.concatTransform( M44f.createTranslated( V3f( 1, 0, 0 ) ) )
		self.assert_( r.getTransform().equalWithAbsError( M44f.createTranslated( V3f( 1, 0, 0 ) ), 1e-4 ) )
		# confirm that setting the world space transform does not affect the camera matrix (that was already set in openGL )
		r.setTransform( M44f.createTranslated( V3f( 0, 1, 0 ) ) )
		self.assert_( r.getTransform().equalWithAbsError( M44f.createTranslated( V3f( 0, 1, 0 ) ), 1e-4 ) )
		r.worldEnd()

	def testTransformsInDeferredRenderer( self ):
		r = Renderer()
		r.setOption( "gl:mode", StringData( "deferred" ) )
		r.transformBegin()
		r.concatTransform( M44f.createRotated( V3f( 1, 1, 1 ) ) )
		r.camera( "main", { "resolution" : V2iData( V2i( 512 ) ), "projection" : StringData( "perspective" ) } )
		r.transformEnd()
		r.worldBegin()
		# confirm that the camera transformation is not affecting the world space matrix
		self.assert_( r.getTransform().equalWithAbsError( M44f(), 1e-4 ) )
		r.concatTransform( M44f.createTranslated( V3f( 1, 0, 0 ) ) )
		r.concatTransform( M44f.createRotated( V3f( 1, 1, 1 ) ) )
		m = r.getTransform()
		r.transformBegin()
		if True:
			# confirm that the transformBegin did not change the current transform
			self.assert_( r.getTransform().equalWithAbsError( m, 1e-4 ) )
			# confirm that concatenate transform works
			r.concatTransform( M44f.createTranslated( V3f( 1, 0, 0 ) ) )
			self.assert_( r.getTransform().equalWithAbsError( M44f.createTranslated( V3f( 1, 0, 0 ) ) * m, 1e-4 ) )
			r.concatTransform( M44f.createScaled( V3f(0.5) ) )
			self.assert_( r.getTransform().equalWithAbsError( M44f.createScaled( V3f(0.5) ) * M44f.createTranslated( V3f( 1, 0, 0 ) ) * m, 1e-4 ) )

			# confirm that setting the world space transform works too
			m2 = M44f.createTranslated( V3f( 0, 1, 0 ) )
			r.setTransform( m2 )
			self.assert_( r.getTransform().equalWithAbsError( m2, 1e-4 ) )

			r.attributeBegin()
			if True:
				# confirm that the attributeBegin did not change the current transform
				self.assert_( r.getTransform().equalWithAbsError( m2, 1e-4 ) )
				# confirm that setting the world space transform works too
				r.setTransform( M44f.createRotated( V3f( 3, 1, 0 ) ) )
				self.assert_( r.getTransform().equalWithAbsError( M44f.createRotated( V3f( 3, 1, 0 ) ), 1e-4 ) )
			r.attributeEnd()
			# confirms that attributeEnd recovers the matrix.
			self.assert_( r.getTransform().equalWithAbsError( m2, 1e-4 ) )

		r.transformEnd()
		# confirms that transformEnd recovers the matrix.
		self.assert_( r.getTransform().equalWithAbsError( m, 1e-4 ) )
		
		r.worldEnd()

	def testInstances(self):
		
		r = Renderer()
		r.instanceBegin( "instanceA", {} )
		r.concatTransform( M44f.createTranslated( V3f( 1, 0, 0 ) ) )
		r.transformBegin()
		r.concatTransform( M44f.createTranslated( V3f( 1, 0, 0 ) ) )
		r.geometry( "sphere", {}, {} )
		r.concatTransform( M44f.createTranslated( V3f( 1, 0, 0 ) ) )
		r.geometry( "sphere", {}, {} )
		r.transformEnd()
		r.concatTransform( M44f.createTranslated( V3f( -1, 0, 0 ) ) )
		r.geometry( "sphere", {}, {} )
		r.instanceEnd()

		r.instanceBegin( "instanceB", {} )
		r.concatTransform( M44f.createTranslated( V3f( 0, 0, 10 ) ) )
		r.instance( "instanceA" )
		r.concatTransform( M44f.createTranslated( V3f( 0, 0, 20 ) ) )
		r.instance( "instanceA" )
		r.instanceEnd()

		r.setOption( "gl:mode", StringData( "deferred" ) )
		r.worldBegin()
		r.concatTransform( M44f.createTranslated( V3f( 0, 5, 0 ) ) )
		r.instance( "instanceB" )
		r.setTransform( M44f.createTranslated( V3f( 0, 10, 0 ) ) )
		r.instance( "instanceB" )
		r.worldEnd()

		g = r.scene().root()

		self.assertEqual( self.__countChildrenRecursive( g ), 12 )
		self.assert_( g.bound().min.equalWithAbsError( V3f( -1, 4, 9 ), 0.001 ) )
		self.assert_( g.bound().max.equalWithAbsError( V3f( 4, 11, 31 ), 0.001 ) )
	
	def tearDown( self ) :

		files = [
			os.path.dirname( __file__ ) + "/output/testPrimVars.tif",
			os.path.dirname( __file__ ) + "/output/testImage.tif",
			os.path.dirname( __file__ ) + "/output/testStackBug.tif",
			os.path.dirname( __file__ ) + "/output/proceduralTest.tif",
		]

		for f in files :
			if os.path.exists( f ) :
				os.remove( f )

if __name__ == "__main__":
    unittest.main()
