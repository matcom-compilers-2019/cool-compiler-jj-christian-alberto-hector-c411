class BinaryTreeNode {
	leftNode : BinaryTreeNode;
	rightNode : BinaryTreeNode;
	key: Int;
	value: Int;
	setValueAndKey(key: Int, value: Int): BinaryTreeNode {
		{
			value <- value;
			key<- key;			
			self;
		}
	};
	getKey(): Int {
		key
	};
	getValue(): Int {
		value
	};
	setKey(newKey: Int): Int {
		key<- newKey
	};
	setValue(newValue: Int): Int {
		value <- newValue
	};
	setLeftNode(leftNode: BinaryTreeNode) : BinaryTreeNode {
		leftNode <- leftNode;
	};
	setRightNode(rightNode: BinaryTreeNode) : BinaryTreeNode {
		rightNode <- rightNode;
	};
	getLeftNode() : BinaryTreeNode {
		leftNode
	};
	getRightNode() : BinaryTreeNode {
		rightNode
	};
};
class BinaryTree {
	RootNode : BinaryTreeNode;
	io : IO <- new IO;
	insert(key: Int, value: Int): BinaryTreeNode {
		insert_recursive(key, value, RootNode, void, true)
	};
	insert_recursive(key: Int, value: Int, 
		currentNode: BinaryTreeNode, parentNode: BinaryTreeNode, leftDir: Bool) : BinaryTreeNode {
		if isvoid currentNode
		then
			let node : BinaryTreeNode <- new BinaryTreeNode in
			{
				node.setValueAndKey(key, value);
				if not isvoid parentNode
				then
				{
					if leftDir
					then
						parentNode.setLeftNode(node);
					else
						parentNode.setRightNode(node);
					fi;
					node;
				}
				else
					RootNode <- node
				fi;
			}
		else
			if (key<= currentNode.getKey())
			then
				insert_recursive(key, value, currentNode.getRightNode(), currentNode, false)
			else
				insert_recursive(key, value, currentNode.getLeftNode(), currentNode, true)
			fi
		fi
	};
	find(key: Int): BinaryTreeNode {
		find_recursive(key, RootNode)
	};
	find_recursive(key: Int, node: BinaryTreeNode): BinaryTreeNode {
		if isvoid node
		then
			void
		else
			if key= node.getKey()
			then
				node
			else
				if key< node.getKey()
				then
					find_recursive(key, node.getRightNode());
				else
					find_recursive(key, node.getLeftNode());
				fi
			fi
		fi
	};
	delete(key: Int): Object {
		delete_recursive(key, RootNode, void, true)
	};
	delete_recursive(key: Int, node: BinaryTreeNode, parentNode: BinaryTreeNode, leftDir: Bool): Object {
		if isvoid node
		then
			void
		else
			if key= node.getKey()
			then
				if isvoid node.getRightNode()
				then
					if isvoid node.getLeftNode()
					then
						-- ����� ����� ���.
						replace_node_in_parent(parentNode, void, leftDir)
					else
						-- ��� ������� �������.
						replace_node_in_parent(parentNode, node.getLeftNode(), leftDir)
					fi
				else
					if isvoid node.getLeftNode()
					then
						-- ��� ������ �������.
						replace_node_in_parent(parentNode, node.getRightNode(), leftDir)
					else
						-- ��� ������� ����.
						let min_node_parent: BinaryTreeNode <- find_min_node_parent(node.getRightNode(), node),
							min_node: BinaryTreeNode <- min_node_parent.getLeftNode() in
						{
							node.setKey(min_node.getKey());
							delete_recursive(min_node.getKey(), min_node, min_node_parent, true);
						}
					fi
				fi
			else
				if key<= node.getKey()
				then
					delete_recursive(key, node.getRightNode(), node, false)
				else
					delete_recursive(key, node.getLeftNode(), node, true)
				fi
			fi
		fi
	};
	find_min_node_parent(node: BinaryTreeNode, parent_node: BinaryTreeNode): BinaryTreeNode {
		if not isvoid node.getLeftNode()
		then
			find_min_node_parent(node.getLeftNode(), node)
		else
			parent_node
		fi
	};
	replace_node_in_parent(parentNode: BinaryTreeNode, node: BinaryTreeNode, leftDir: Bool): BinaryTreeNode {
		if not isvoid parentNode
		then
			if leftDir
			then
				parentNode.setLeftNode(node)
			else
				parentNode.setRightNode(node)
			fi
		else
			RootNode <- node
	}
	print(): BinaryTree {
		print_node(RootNode)
	};
	print_node(node: BinaryTreeNode) : BinaryTree {
		{
			io.out_int(node.getKey());
			io.out_string(": ");
			let leftNode: BinaryTreeNode <- node.getLeftNode(), rightNode: BinaryTreeNode <- node.getRightNode() in
			{
				if isvoid leftNode
				then
					io.out_string("null ")
				else
				{
					io.out_int(leftNode.getKey());
					io.out_string(" ");
				}
				fi;	
				if isvoid rightNode
				then
					io.out_string("null ")
				else
				{
					io.out_int(rightNode.getKey());
					io.out_string(" ");
				}
				fi;
				io.out_string("\n");	
				if not isvoid leftNode
				then
					print_node(leftNode)
				else
					leftNode
				fi;
				if not isvoid rightNode
				then
					print_node(rightNode)
				else
					rightNode
				fi;
			};
			self;
			self;
		}
	};
};
class Main {
	io: IO <- new IO;
	tree: BinaryTree <- new BinaryTree;
	main(): Object {
		{
			tree.insert(8, 8);
			tree.insert(3, 3);
			tree.insert(10, 10);
			tree.insert(1, 1);
			tree.insert(6, 6);
			tree.insert(9, 9);
			tree.insert(14, 14);
			tree.insert(4, 4);
			tree.insert(7, 7);
			tree.insert(13, 13);
			io.out_string("result tree:\n");
			tree.print();
			io.out_string("\n");
			let findNode: BinaryTreeNode  <- tree.find(5) in
				if isvoid findNode
				then
					io.out_string("key'5' does not found\n")
				else
				{
					io.out_string("value of key'5' is ");
					io.out_int(findNode.getValue());
				}
				fi;
			
			let findNode: BinaryTreeNode <- tree.find(13) in
				if isvoid findNode
				then
					io.out_string("key'13' does not found\n")
				else
				{
					io.out_string("value of key'13' is ");
					io.out_int(findNode.getValue());
io.out_string("\n");
				}
				fi;
			let findNode: BinaryTreeNode <- tree.find(8) in
				if isvoid findNode
				then
					io.out_string("key'8' does not found\n")
				else
				{
					io.out_string("value of key '8' is ");
					io.out_int(findNode.getValue());
				}
				fi;
			io.out_string("\n");
			while true
			loop
			{	
				io.out_string("Enter command (0 - add key, 1 - delete key, 2 - print tree): ");
				let command: Int <- io.in_int() in
				{
					if command = 0
					then
					{				
						io.out_string("Enter number to insertion: ");
						let key: Int <- io.in_int() in
							tree.insert(key, key);
					}
					else
						if command = 1
						then
						{
							io.out_string("Enter number to deletion: ");
							let key: Int <- io.in_int() in
								tree.delete(key);
						}
						else
							tree.print()
						fi
					fi
					io.out_string("\n");
				};
			}
			pool
			io.in_string();
			void;
		}
	};
};