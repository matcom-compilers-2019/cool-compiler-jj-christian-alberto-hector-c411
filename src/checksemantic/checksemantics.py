
# import sys
# sys.path.append('/..')

from parsing import cool_ast as ast
import visitor
from checksemantic.scope import Scope
ERROR = 0

class CheckSemanticsVisitor:
    @visitor.on('node')
    def visit(self, node, scope, errors):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node, scope, errors):
        return self.visit(node.class_list, scope, errors)

    @visitor.when(ast.ClassListNode)
    def visit(self, node, scope, errors):
        result = True
        for c in node.classes:
            methods = [m for m in c.features if isinstance(m, ast.MethodNode)]
            attrs = [m for m in c.features if isinstance(m, ast.AttributeNode)]
            p = 'Object' if not c.parent else c.parent.value
            if not scope.add_type(c.name.value, [], [], parent=p):
                errors.append('Class "%s" cannot be defined twice at line %d, column %d' % (c.name.value, c.name.line, c.name.column))
                return False
            child_scope = scope.create_child_scope(inside=c.name.value)
            for m in methods:
                if not scope.define_method(c.name.value, m):
                    errors.append("Can't define method '%s' in class '%s'. Line %d, column %d" % (m.name.value, c.name.value, m.name.line, m.name.column))
                    result = False
            for a in attrs:
                if not scope.define_attr(c.name.value, a):
                    errors.append("Can't define attribute '%s' in class '%s'. Line %d, column %d" % (a.name.value, c.name.value, a.name.line, a.name.column))
                    result = False
        for c in node.classes:
            child_scope = scope.get_scope_of_type(c.name.value)
            if not self.visit(c, child_scope, errors):
                errors.append("Can't define class '%s'. Line %d, column %d" % (c.name.value, c.name.line, c.name.column))
                result = False
        return result
    
    @visitor.when(ast.ClassNode)
    def visit(self, node, scope, errors):
        result = True
        if node.parent and (node.parent.value == 'Int' or node.parent.value == 'Bool' or node.parent.value == 'String'):
            errors.append("Cannot inherits from '%s' at line %d, column %d" % (node.parent.value, node.parent.line, node.parent.column))
            return ERROR
        if node.parent and not scope.check_type(node.parent.value):
            errors.append('Type %s is not defined at line %d, column %d' %(node.parent.value, node.parent.line, node.parent.column))
        if not node.parent:
            from lark import Token
            node.parent = Token(None, 'Object')
        if scope.inherits(node.parent.value, node.name.value, 0)[0]:
            errors.append("There is a cyclic inheritance in class %s at line %d, column %d" % (node.name.value, node.name.line, node.name.column))
            return ERROR
        for f in node.features:
            if not self.visit(f, scope, errors):
                errors.append('Error in feature "%s" at line %d, column %d' % (f.name.value, f.name.line, f.name.column))
                result = False
        return result
    
    @visitor.when(ast.AttributeNode)
    def visit(self, node, scope, errors):
        val_t = scope.true_type(node.type.value)
        if not scope.check_type(val_t):
            errors.append("Can't define attribute '%s' because '%s' doesn't exists at line %d, column %d"%(node.name.value, node.type.value, node.name.line, node.name.column))
            return ERROR
        t = None
        if node.value:
            t = self.visit(node.value, scope, errors)
            if not t:
                return ERROR
        if t:
            val_t = scope.true_type(val_t)
            if not (scope.inherits(t,val_t,0)[0]):
                errors.append('Attribute declaration failed because the types do not match at line %d column %d' % (node.type.line, node.type.column))
                return ERROR
            node.static_type = val_t
            return val_t
        node.static_type = val_t
        return val_t
    
    @visitor.when(ast.MethodNode)
    def visit(self, node, scope, errors):
        child_scope = scope.create_child_scope()
        child_scope.methods = [m for m in scope.methods]
        fine = True
        if node.return_type.value != 'SELF_TYPE' and not child_scope.check_type(node.return_type.value):
            errors.append('Method declaration failed because the return type is not defined at line %d column %d' %(node.return_type.line, node.return_type.column))
            fine = False
        for p in node.params:
            if not self.visit(p, child_scope, errors):
                fine = False
        
        if not fine:
            return ERROR
        
        fine = self.visit(node.body, child_scope, errors)
                
        t = child_scope.true_type(node.return_type.value)

        fine = child_scope.true_type(fine)
        if not scope.inherits(fine, t, 0)[0]:
            errors.append('The return type does not match with the expression in the body of method %s at line %d, column %d' % (node.name.value, node.return_type.line, node.return_type.column))
            return ERROR
        scope.add_method(node)
        node.static_type = fine
        return fine
    
    @visitor.when(ast.ParamNode)
    def visit(self, node, scope, errors):
        if not scope.check_type(node.type.value):
            errors.append('Parameter declaration failed because the type is not defined at line %d column %d' % (node.type.line, node.type.column))
            return False
        if node.type.value == 'SELF_TYPE':
            errors.append('Parameter cannot be "SELF_TYPE" at line %d, column %d' % (node.type.line, node.type.column))
            return ERROR
        scope.define_param(node.name.value, node.type.value)
        node.static_type = node.type.value
        return node.type.value

    @visitor.when(ast.ComparerNode)
    def visit(self, node, scope, errors):
        rleft = self.visit(node.left, scope, errors)
        rright = self.visit(node.right, scope, errors)

        if isinstance(node, ast.EqualNode):
            result = self.visit_equal(scope, rleft, rright, errors)
            if result:
                node.static_type = result
            return result

        if rleft != 'Int' or rright != 'Int':
            errors.append('Operator error: the operand types do not match. Both operands must be "INTEGER"')
            return ERROR
        node.static_type = 'Bool'
        return 'Bool'

    def visit_equal(self, scope, rleft, rright, errors):
        if rleft == 'Int' or rleft == 'String' or rleft == 'Bool' or rright == 'Int' or rright == 'String' or rright == 'Bool':
            if rleft != rright:
                errors.append("Operator error: the operand types must be the same when one of them is a basic type on equality")
                return False
        return 'Bool'

    @visitor.when(ast.ArithmeticNode)
    def visit(self, node, scope, errors):
        rleft = self.visit(node.left, scope, errors)
        rright = self.visit(node.right, scope, errors)
        if rleft != "Int" or rright != "Int":
            errors.append('Operator error: the operand types do not match. Both operands must be "INTEGER"')
            return ERROR
        node.static_type = rleft
        return rleft

    @visitor.when(ast.OpositeNode)
    def visit(self, node, scope, errors):
        expr_type = self.visit(node.expr, scope, errors)
        if expr_type != "Int" :
            errors.append('The "~" operator takes an INTEGER expression as parameter, "%s" was given' % (expr_type))
            return ERROR
        node.static_type = expr_type
        return expr_type

    @visitor.when(ast.NotNode)
    def visit(self, node, scope, errors):
        expr_type = self.visit(node.expr, scope, errors)
        if expr_type != "Bool" :
            errors.append('The "not" operator takes a BOOLEAN expression as parameter, "%s" was given' % (expr_type))
            return ERROR
        node.static_type = expr_type
        return expr_type

    @visitor.when(ast.LetNode)
    def visit(self, node, scope, errors):
        child_scope = scope.create_child_scope()
        for dcl in node.let_part:
            self.visit(dcl, child_scope, errors, let=True)
        result = self.visit(node.in_part, child_scope, errors)
        if result:
            node.static_type = result
        return result

    @visitor.when(ast.BlockNode)
    def visit(self, node, scope, errors):
        child_scope = scope.create_child_scope()
        rtype = True
        for expr in node.exprs:
            rtype = self.visit(expr, child_scope, errors)
            if not rtype:
                return ERROR
        node.static_type = rtype
        return rtype

    @visitor.when(ast.AssignationNode)
    def visit(self, node, scope, errors):
        rtype = self.visit(node.value, scope, errors)
        if not scope.is_defined(node.name.value):
            errors.append('Variable "%s" not defined at line %d column %d.' % (node.name.value, node.name.line, node.name.column))
            return ERROR
        if rtype != 'Void' and not scope.inherits(rtype, scope.get_type(node.name.value), 0):
            errors.append('Assignation failed due to the type of the variable  "%s" and the type of the assigned expression do not match at line %d column %d' % (node.name.value, node.name.line, node.name.column))
            return ERROR
        node.static_type = rtype
        return rtype

    @visitor.when(ast.NumberNode)
    def visit(self, node, scope, errors):
        node.static_type = 'Int'
        return "Int"

    @visitor.when(ast.BoolNode)
    def visit(self, node, scope, errors):
        node.static_type = 'Bool'
        return "Bool"
    
    @visitor.when(ast.StrtingNode)
    def visit(self, node, scope, errors):
        node.static_type = 'String'
        return "String"

    @visitor.when(ast.VarNode)
    def visit(self, node, scope, errors):
        if not scope.is_defined(node.id.value):
            errors.append('Variable "%s" not defined at  line %s column %s.' % (node.id.value, node.id.line, node.id.column))
            return ERROR
        result = scope.get_type(node.id.value)
        if result:
            node.static_type = result
        return result

    @visitor.when(ast.DeclarationNode)
    def visit(self, node, scope, errors, let=False):
        rtype = node.type.value

        if not scope.check_type(rtype):
            errors.append("Declaration of '%s' failed because '%s' doesn't exist at line %d, column %d" % (node.name.value, node.type.value, node.name.line, node.name.column))
            return ERROR
        t = None
        if node.expr:
            t = self.visit(node.expr, scope, errors)
            if not t:
                errors.append('Declaration failed because the assigned expression is not defined at line %d column %d' % (node.name.line, node.name.column))

        t = scope.true_type(node.type.value)
        if not scope.inherits(t, rtype, 0):
            errors.append('Declaration failed because the type of the variable and the type of the expression do not match at line %d column %d' % (node.name.line, node.name.column))
            return ERROR
        
        if let:
            result = scope.define_for_let(node.name.value, node.type.value)
            if result:
                node.static_type = result

        if scope.is_local(node.name.value) and not let:
            errors.append('Variable "%s" already defined at line:%d column:%d.' % (node.name.value, node.name.line, node.name.column))
            return ERROR
        
        scope.define_variable(node.name.value, t) if rtype != 'Void' else scope.define_variable(node.name.value, 'Void')
        node.static_type = rtype
        return rtype
    
    @visitor.when(ast.NewNode)
    def visit(self, node, scope, errors):
        if not scope.check_type(node.type.value):
            errors.append('Type "%s" not defined at line %d column %d' % (node.type.value, node.type.line, node.type.column))
            return ERROR

        result = scope.true_type(node.type.value)
        node.static_type = result
        return result
    
    @visitor.when(ast.LoopNode)
    def visit(self, node, scope, errors):
        cvisit = self.visit(node.condition, scope, errors)
        if not scope.inherits(cvisit, 'Bool', 0)[0]:
            errors.append('The condition in while loop must be "BOOLEAN".')
            return ERROR
        child_scope = scope.create_child_scope()
        result = self.visit(node.body, child_scope, errors)
        if not cvisit or not result:
            return ERROR
        else:
            node.static_type = 'Void'
            return 'Void'
    
    @visitor.when(ast.ConditionalNode)
    def visit(self, node, scope, errors):
        _if = self.visit(node.if_part, scope, errors)
        
        if not scope.inherits(_if,'Bool',0)[0]:
            errors.append('IF expression must be "BOOLEAN".')
        
        child_scope = scope.create_child_scope()
        _then = self.visit(node.then_part, child_scope, errors)
        child_scope = scope.create_child_scope()
        _else = self.visit(node.else_part, child_scope, errors)
        if not _if or not _then or not _else:
            return ERROR
        result = scope.join(_then, _else)
        node.static_type = result
        return result
    
    def arguments_checker(self, method, node, scope, errors):
        if len(node.params) != len(method.params):
            errors.append('Method "%s" receives %d parameters, %d was given at line %d, column %d.'%(method.name.value, len(method.params), len(node.params), node.method_name.line, node.method_name.column))
            return False
        
        if len(node.params) == 0:
            return True
       
        result = True
        for i in range(len(node.params)):
            arg_t = self.visit(node.params[i], scope, errors)
            if not arg_t:
                errors.append("Parameter '%s' not defined."%(method.params[i].name.value))
                result = False
            param_t = method.params[i].type.value
            if arg_t != 'Void' and not scope.inherits(arg_t, param_t, 0)[0]:
                errors.append('The type of parameter "%s" does not match' % (method.params[i].name.value))
                result = False
        return result
        
    @visitor.when(ast.ShortDispatchNode)
    def visit(self, node, scope, errors):
        method = scope.is_defined_in_type(scope.inside,node.method_name.value)
        if not method:
            errors.append('Method "%s" not defined at line %d column %d' % (node.method_name.value, node.method_name.line, node.method_name.column))
            return ERROR
        if not self.arguments_checker(method, node, scope, errors):
            return ERROR
        
        result = scope.true_type(method.return_type.value)
        node.static_type = result
        return result

    @visitor.when(ast.PointDispatchNode)
    def visit(self, node, scope, errors):
        t = self.visit(node.expr, scope, errors)
        if not t:
            return ERROR
        m = scope.look_for_method(t,node.method_name.value)
        if not m:
            errors.append('Method "%s" not defined at line %d column %d' % (node.method_name.value, node.method_name.line, node.method_name.column))
            return ERROR
        if not self.arguments_checker(m, node, scope, errors):
            return ERROR
        sc = scope.get_scope_of_type(t)
        result = sc.true_type(m.return_type.value)
        node.static_type = result
        return result
    
    @visitor.when(ast.ParentDispatchNode)
    def visit(self, node, scope, errors):
        t = self.visit(node.expr, scope, errors)
        if not scope.inherits(t, node.parent.value, 0)[0]:
            return ERROR
        m = scope.look_for_method(node.parent.value, node.method_name.value)
        if not m:
            errors.append('Method "%s" not defined at line %d column %d' % (node.method_name.value, node.method_name.line, node.method_name.column))
            return ERROR
        if not self.arguments_checker(m, node, scope, errors):
            return ERROR
        sc = scope.get_scope_of_type(node.parent.value)
        result = sc.true_type(m.return_type.value)
        node.static_type = result
        return result

    @visitor.when(ast.IsVoidNode)
    def visit(self, node, scope, errors):
        if not self.visit(node.expr, scope, errors):
            return ERROR
        node.static_type = 'Bool'
        return 'Bool'
    
    @visitor.when(ast.CaseNode)
    def visit(self, node, scope, errors):
        maint = self.visit(node.main_expr, scope, errors)
        if not maint:
            return ERROR
        if maint == 'Void':
            errors.append("Main expression on 'CASE' can't be 'VOID'.")
            return ERROR

        result = ERROR
        selected_branch = None
        minLevel = 100100
        for b in node.branches:
            btype = b.type.value
            t, level = scope.inherits(maint, btype, 0)
            if t and level < minLevel:
                selected_branch = b    
                minLevel = level
        if not selected_branch:
            errors.append("At least one branch must be selected on 'CASE' expression")
            return ERROR
        self.visit(ast.DeclarationNode(selected_branch.id, selected_branch.type, node.main_expr), scope, errors, let=True)
        result = self.visit(selected_branch, scope, errors)
        if not result:
                errors.append("Error in expression of branch %s at line %d, column %d" % (b.id.value, b.id.line, b.id.column))
                return ERROR
        node.static_type = result
        return result
    
    @visitor.when(ast.BranchNode)
    def visit(self, node, scope, errors):
        rtype = self.visit(node.expr, scope, errors)
        if not rtype:
            errors.append('Error on branch because the assigned expression is not defined at line %d column %d' % (node.id.line, node.id.column))
            return ERROR
        node.static_type = rtype
        return rtype

    @visitor.when(ast.VoidNode)
    def visit(self, node, scope, errors):
        node.static_type = 'Void'
        return 'Void'