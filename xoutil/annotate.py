#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.annotate
#----------------------------------------------------------------------
# Copyright (c) 2012 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License (GPL) as published by the
# Free Software Foundation;  either version 2  of  the  License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Created on Apr 3, 2012

'''
Provides a forward-compatible (PEP 3107) annotations.
'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)
                        
__docstring_format__ = 'rst'
__author__ = 'manu'


from xoutil.decorators import decorator
from xoutil.iterators import first

@decorator
def annotate(func, signature=None, **keyword_annotations):
    '''
    Annotates a function with a forward-compatible internal form (i.e, injects
    a `__annotations__` mapping to the function.)
    
    You may pass the following arguments:
    
    - [Not yet implemented] A single string with the equivalent signature of the
      function::
    
         >>> @annotate('(a: "some argument", *args: "positional arguments") -> list')
         ... def somefunction(a, *args):
         ...    pass
         
         >>> somefunction.__annotations__.get('a')
         'some argument'
         
         >>> somefunction.__annotations__.get('return') is list
         True
             
      In this case there are several limitations (and deviations) from the PEP
      3107 text:
      
      - There's no support for the full python expressions. 
      
      - There's no support for nested arguments support (since this feature is
        also deprecated).
        
      - Specifying defaults is no supported (nor needed).
      
    - Several keyword arguments with each of the annotations. Since you can't
      include the 'return' keyword argument for the annotation related with the
      return of the function, we provide several alternatives: if any of the
      following keywords arguments is provided (tested in the given order):
      'return_annotation', '_return', '__return'; then it will be considered the
      'return' annotation, the rest will be regarded as other annotations.

      The previous example would be like this::
      
          >>> @annotate(a="some argument", args="positional arguments", return_annotation=list)
          ... def otherfunc(a, *args):
          ...    pass

          >>> otherfunc.__annotations__.get('a')
          'some argument'
            
          >>> otherfunc.__annotations__.get('return') is list
          True
          
    In any of the previous cases, you may provide more (or less) annotations
    than possible by following the PEP syntax. This is not considered an error,
    since the PEP allows annotations to be modified by others means.
    
    If you provide a signature string **and** keywords annotations, the keywords
    will take precedence over the signature::
    
        >>> @annotate('() -> list', return_annotation=tuple)
        ... def otherfunction():
        ...    pass
        
        >>> otherfunction.__annotations__.get('return') is list
        False
        
        >>> otherfunction.__annotations__.get('return') is tuple
        True
    '''
    func.__annotations__ = annotations = getattr(func, '__annotations__', {})
    if signature:
        raise NotImplemented('Parsing signatures is not yet implemented')
    return_annotation_kwarg = first(lambda k: k in ('return_annotation', '_return', '__return'), keyword_annotations)
    if return_annotation_kwarg:
        annotations['return'] = keyword_annotations[return_annotation_kwarg]
        del keyword_annotations[return_annotation_kwarg]
    annotations.update(keyword_annotations)
    return func
