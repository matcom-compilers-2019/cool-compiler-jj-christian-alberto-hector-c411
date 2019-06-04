from lark import Lark, Token
from parsing import grammar, cool_ast, preprocess
from parsing.cool_transformer import ToCoolASTTransformer
from checksemantic.checksemantics import CheckSemanticsVisitor
from checksemantic.scope import Scope

#TODO: Find all the errors in this test, or move on and try to figure out what is wrong using another test.
#TODO: A parameter hides the definition of an attribute

# program = r"""

# (*class C inherits A{
#   zzzzz(a:Int, b:Bool):String{
#     5
#   };
# };*)
# --Class A
# class A{ 
#     --Returns itself
    
#     clone(c : A):SELF_TYPE{
#         self
#     };
    
#     m(a:Int, b:Bool):Int{
#         4
#     };
    
#     t():Int{
#         m(3,true)
#     } ;
# };
# (*Let's test the multiline comments
# A ver q pasa.

# *)
# --Class B
# class B inherits A{
#     n():Int{
#         {
#             clone(self);
#             5;
#         }
#     };
# };

# --Entry point
# class Main{ 
#     main():Int{ 
#         { 
#             ss : String <- "string";
#             x : A <- new A;
#             x.t();
#             b : Bool <- 4 < x.t();
#             y : A <- new B;
#             y@A.t();
#             v : Int <- 4 + ~let t : Int <- 5 in t + 5;
#             case v of s : Int => if true then 5 + 5 else "s" fi; esac; 
#             0;
#         } 
#     }; 
# };
# """

program = r"""
class Main {
  x : Int;
  main() : Object {
    (new IO). out_string(while (x < 10) loop x <- x + 1 pool.type_name())
  };
};
"""

parser = Lark(grammar.grammar, start='program')
print('PARSER CREATED')

preprocessed = preprocess.preprocess_program(program)
print('KEYWORDS POINTED AND COMMENTS ERASED')
print(preprocessed)

tree = parser.parse(preprocessed)
print(tree.pretty())
ast = ToCoolASTTransformer().transform(tree)
print('AST CREATED')
checkSemanticVisitor = CheckSemanticsVisitor()
scope = Scope()
errors = []
t = checkSemanticVisitor.visit(ast, scope, errors)
print(t)
for error in errors:
    print(error)

# ln = 0
# line = ""
# for c in preprocessed:
#   line += c
#   if c == '\n':
#     ln+=1
#     if ln == 323:
#       print(line)
#     else:
#       line = ""