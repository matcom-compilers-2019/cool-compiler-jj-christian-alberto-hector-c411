from code_gen.transpilator import codeVisitor

from lark import Lark, Token
from parsing import grammar, cool_ast, preprocess
from parsing.cool_transformer import ToCoolASTTransformer
from checksemantic.checksemantics import CheckSemanticsVisitor
from checksemantic.scope import Scope
from cool import fetch_program

import os, sys

###TODO: AVERIGUAR COMO PUEDO HACER PARA CONTROLAR QUE LOS NOMBRES DE LAS VARIABLES NO SEAN RESERVED WORDS

# program = r"""
# class Main{
#     main():INT{2+2}
# };
# """

program = r"""
(* models one-dimensional cellular automaton on a circle of finite radius
   arrays are faked as Strings,
   X's respresent live cells, dots represent dead cells,
   no error checking is done *)
class CellularAutomaton inherits IO {
    population_map : String;
   
    init(map : String) : SELF_TYPE {
        {
            population_map <- map;
            self;
        }
    };
   
    print() : SELF_TYPE {
        {
            out_string(population_map.concat("\n"));
            self;
        }
    };
   
    num_cells() : Int {
        population_map.length()
    };
   
    cell(position : Int) : String {
        population_map.substr(position, 1)
    };
   
    cell_left_neighbor(position : Int) : String {
        if position = 0 then
            cell(num_cells() - 1)
        else
            cell(position - 1)
        fi
    };
   
    cell_right_neighbor(position : Int) : String {
        if position = num_cells() - 1 then
            cell(0)
        else
            cell(position + 1)
        fi
    };
   
    (* a cell will live if exactly 1 of itself and it's immediate
       neighbors are alive *)
    cell_at_next_evolution(position : Int) : String {
        if (if cell(position) = "X" then 1 else 0 fi
            + if cell_left_neighbor(position) = "X" then 1 else 0 fi
            + if cell_right_neighbor(position) = "X" then 1 else 0 fi
            = 1)
        then
            "X"
        else
            "."
        fi
    };
   
    evolve() : SELF_TYPE {
        (let position : Int in
        (let num : Int <- num_cells() in
        (let temp : String in
            {
                while position < num loop
                    {
                        temp <- temp.concat(cell_at_next_evolution(position));
                        position <- position + 1;
                    }
                pool;
                population_map <- temp;
                self;
            }
        ) ) )
    };
};

class Main {
    cells : CellularAutomaton;
   
    main() : SELF_TYPE {
        {
            cells <- (new CellularAutomaton).init("         X         ");
            cells.print();
            (let countdown : Int <- 20 in
                while 0 < countdown loop
                    {
                        cells.evolve();
                        cells.print();
                        countdown <- countdown - 1;
                    }
                pool
            );
            self;
        }
    };
};
"""
# parser = Lark(grammar, start='program')
# print('PARSER CREATED')
# tree = parser.parse(program)
# print(tree.pretty())
# ast = ToCoolASTTransformer().transform(tree)
# print('AST CREATED')
# checkSemanticVisitor = CheckSemanticsVisitor()
# scope = Scope()
# errors = []
# t = checkSemanticVisitor.visit(ast, scope, errors)
# print(t)
# for error in errors:
#     print(error)

def A():
    parser = Lark(grammar.grammar, start='program')

    preprocessed = preprocess.preprocess_program(program)
    tree = parser.parse(preprocessed)
    ast = ToCoolASTTransformer().transform(tree)
    checkSemanticVisitor = CheckSemanticsVisitor()
    scope = Scope()
    errors = []
    t = checkSemanticVisitor.visit(ast, scope, errors)
    return ast
