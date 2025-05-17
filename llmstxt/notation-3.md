Title: Notation 3 Logic

URL Source: https://www.w3.org/DesignIssues/Notation3

Markdown Content:
Tim Berners-Lee, August 2005

$Revision: 1.154 $ of $Date: 2024/02/16 13:03:01 $

 Status: An early draft of a semi-formal semantics of the N3 logical properties. 
Up to Design Issues

### An RDF language for the Semantic Web

* * *

![Image 1: n3](file:///home/RDF/icons/n3_small)

This article gives an operational semantics for Notation3 (N3) and some RDF properties for expressing logic.These properties, together with N3's extensions of RDF to include variables and nested graphs, allow N3 to be used to express rules in a web environment.

This is an informal semantics in that should be understandable by a human being but is not a machine readable formal semantics. This document is aimed at a logician wanting to a reference by which to compare N3 Logic with other languages, and at the engineer coding an implementation of N3 Logic and who wants to check the detailed semantics.

These properties are not part of the N3 language, but are properties which allow N3 to be used to express rules, and rules which talk about the provenance of information, contents of documents on the web, and so on. Just as OWL is expressed in RDF by defining properties, so rules, queries, differences, and so on can be expressed in RDF with the N3 extension to formulae.

The log: namespace has functions, which have built-in meaning for CWM and other software.

See also:

*   [The schema for the log: namespace](https://www.w3.org/2000/10/swap/log.n3)
*   [A vocabulary for expressing differences between RDF graphs](https://www.w3.org/DesignIssues/Diff.html)
*   [a formal design for RDF/N3 context/scopes](http://lists.w3.org/Archives/Public/www-rdf-logic/2001Sep/0004.html)

 Dan Connolly to www-rdf-logic, Thu, Sep 06 2001

The prefix log:is used below as shorthand for the namespace <[http://www.w3.org/2000/10/swap/log#](https://www.w3.org/2000/10/swap/log#)>. See the [schema](https://www.w3.org/2000/10/swap/logic.n3) for a summary.

Motivation
----------

 The motivation of the logic was to be useful as a tool in in open web environment. The Web contains many sources of information, with different characteristics and relationships to any given reader.Whereas a closed system may be built based on a single knowledge base of believed facts, an open web-based system exists in an unbounded sea of interconnected information resources. This requires that an agent be aware of the provenance of information, and responsible for its disposition.The language for use in this environment typically requires the ability to express what document or message said what, so the ability to quote subgraphs and match them against variable graphs is essential.This quotation and reference, with its inevitable possibility of direct or indirect self-reference, if added directly to first order logic presents problems such as paradox traps. To avoid this, N3 logic has deliberately been kept to limited expressive power: it currently contains no general first order negation.Negated forms of many of the built-in functions are available, however.
A goal is that information, such as but not limited to rules, which requires greater expressive power than the RDF graph, should be sharable in the same way as RDF can be shared.This means that one person should be able to express knowledge in N3 for a certain purpose, and later independently someone else reuse that knowledge for a different unforeseen purpose.As the context of the later use is unknown, this prevents us from making implicit closed assumptions about the total set of knowledge in the system as a whole.

Further, we require that other users of N3 in the web can express new knowledge without affecting systems we have already built. This means that N3 must be fundamentally monotonic: the addition of new information from elsewhere, while it might cause an inconsistency by contradicting the old information (which would have to be resolved before the combined system is used), the new information cannot silently change the meaning of the original knowledge.

The non-monotonicity of many existing systems follows from a form of negation as failure in which a sentence is deemed false if it not held within (or, derivable from) the current knowledge base.It is this concept of current knowledge base,which is a variable quantity, and the ability to indirectly make reference to it which causes the non-monotonicity.In N3Logic, while a current knowledge base is a fine concept, there is no ability to make reference to it implicitly in the negative. The negation provided is the ability only for a specific given document (or, essentially, some abstract formula) to objectively determine whether or not it holds, or allows one to derive, a given fact.This has been called Scoped Negation As Failure (SNAF).

Formal syntax
-------------

 The syntax of N3 is defined by the [context-free grammar](https://www.w3.org/2000/10/swap/grammar/n3-report.html)This is available in machine-readable form in [Notation3](https://www.w3.org/2000/10/swap/grammar/n3.n3) and[RDF/XML.](https://www.w3.org/2000/10/swap/grammar/n3.rdf)
The top-level production for an N3 document is <http://www.w3.org/2000/10/swap/grammar/n3#document>.

In the semantics below we will consider these productions using notation as follows.

| Production | N3 syntax examples | notation below for instances |
| --- | --- | --- |
| symbol | <foo#bar><http://example.com/> | c d e f |
| variable | Any symbol quantified by @forAll or @forSome in the same or an outer formula. | x y z |
| formula | { ... }or an entire document | F G H K |
| set of universal variables of F | @forAll :x, :y. | uvF |
| set of existential variables of F | @forSome :z, :w. | evF |
| set of statements of F |  | stF |
| statement | <#myCar><#color> "green". | F i or {s p o} |
| string | "hello world" | s |
| integer | 34 | i |
| list | ( 1 2 ?x <a> ) | L M |
| Element i of list L |  | L i |
| length of list |  | |L| |
| expression | see grammar | n m |
| Set* | {$ 1, 2, <a> $} | S T |

 *The set syntax and semantics are not part of the current Notation3 language but are under consideraton.

Semantics
---------

Note.The Semantics of a generic RDF statement are not defined here.The extensibility of RDF is deliberately such that a document may draw on predicates from many sources.The statement {n c m} expresses that the relationship denoted by c holds between the things denoted by n and m.The meaning of the statement {n c m} in general is defined by any specification for c. The Architecture of the WWW specifies informally how the curious can discover information about the relation. It discusses how the architecture and management of the WWW is such that a given social entity has jurisdiction over certain symbols (though for example domain name ownership). This philosophy and architecture is not discussed further here.Here though we do define the semantics of certain specific predicates which allow the expression of the language.In analyzing the language the reader is invited to consider statements of unknown meaning ground facts.N3Logic defines the semantics of certain properties. Clearly a system which recognizes further logical predicates, beyond those defined here, whose meaning introduces greater logical expressiveness would change the properties of the logic.
### Simplifications

N3 has a number of types of shortcut syntax and syntactic sugar. For simplicity, in this article we consider a language simpler the full N3 syntax referenced above though just as expressive, in that we ignore most syntactic sugar. The following simplifications are made.
We ignore syntactic sugar of comma and semicolon as shorthand notations.  That is, we consider a simpler language in which any such syntax has been expanded out. Loosely:

| A sentence of the form | becomes two sentences |
| --- | --- |
| subject stuff ; morestuff . | subject stuff . subject morestuff . |
| subject predicate stuff , object . | subject predicate stuff subject predicate object . |

For those familiar with N3, the other simplifications in the language considered here are as follows.

*   prefixes have been expanded and all qualified names replaced with symbols using full URIs between angle brackets.
*   The path syntax which uses "!" and "^" is assumed expanded into its equivalent blank node form;
*   The "is ... of " backwards construction has been replaced by the equivalent forwards direction syntax.
*   The "=" syntax is not used as shorthand for owl:sameAs. In fact, we use = here in the text for value equality.
*   @keywords is not used
*   The @a shorthand for rdf:type is replaced with a direct use of the full URI symbol for rdf:type
*   all ?x forms are replaced with explicit universal quantification in the enclosing parent of the current formula.

 Notation3 has explicitly quantified existential variables as well as blank nodes.The description below does not mention blank nodes, although they are very close in semantics to existentially quantified variables. We consider for now a simpler language in which blank nodes have been replaced by explicitly named variables existentially quantified in the same formula.
We have only included strings and integers, rather than the whole set of RDF types an user-defined types.

These simplifications will not deter us from using N3 shorthand in examples where it makes them more readable, so the reader is assumed familiar with them.

Defining N3 Entailment
----------------------

The RDF specification defines a very weak form of entailment, known as RDF entailment or simple entailment.He we define the equivalent very simple N3-entailment. This does not provide us with useful powers of inference: it is almost textual inclusion, but just has conjunction elimination (statement removal) , universal elimination, existential introduction and variable renaming. Most of this is quite traditional.The only thing to distinguish N3 Logic from typical logics is the Formula, which allows N3 sentences to make statements about N3 sentences. The following details are included for completeness and may be skipped.

### Substitution

Substitution is defined to recursively apply inside compound terms, as is usual.Note only that substitution does descend into compund terms, while substitution of owl:sameAs, discussed later, does not.
We define a substitution operator σ x/m which replaces occurrences of the variable x. with the expression m. For compound terms, substitution of a compound term (list, formula or set) is performed by performing substitution of each component, recursively.

Abbreviating the substitution σ x/m as σ , we define substitution operator as usual:

σ x = m  (x is replaced by m)

 σ y = y(y not equal to x)

 σa = a (symbols and literals are unchanged)

 σi = i

 σs = s 

 σ( a b ... c ) = ( σa σb ... σc )  (substitution goes into compound terms)

 σ{$ a, b, ... c $}  = {$ σa, σb, ... σc $}

 uv σF = σ uvF

 ev σF = σ evF

 st σF = σ stF

In general a substitution operator is the sequential application of single substitutions:

σ=σ x 1/m1 σ x 2/m2 σ x 2/m2 ... σ x n/mn

### Value equality

Value equality between terms is defined in an ordinary way, compatible with RDF.
For concepts which exist in RDF, we use RDF equality. This is RDF node equality. These atomic concepts have a simple form of equality.

For lists, equality is defined as a pairwise matching.

For sets, equality is defined as a mapping between equal terms existing in each direction.

For formulae, equality F = G is defined as a substitution σ existing mapping variables to variables. (Note that as here RDF Blank Nodes are considered as existential variables, the substitution will map b-nodes to b-nodes.)

The table below is a summary for completeness.

| Production | Equality |
| --- | --- |
| symbol | uri is equal unicode string |
| variable | variable name is equal unicode string |
| formula | F = G iff |stF| = |stG| and there is some substitution σ such that(∀i .∃j . σ Fi = σG j.) |
| statement | Subjects are equal, predicates are equal, and objects are equal |
| string | equal unicode string |
| integer | equal integer |
| list L = M | |L| = |M| &(∀i . L i = M i ) |
| set S = T | (∀i .∃j . S i = T j.) &(∀i .∃j . S i = T j.) |
| formula F = G | ∃σ.σ F =σ G |
| unicode string | Unicode strings should be in canonical form. They are equal if the corresponding characters have numerically equal code points. |

### Conjunction

N3, like RDF, has an implied conjunction, with its normal properties, between the statements of a formula.
The semantics of a formula which has no quantifiers (@forAll or @forSome) are the conjunction of the semantics of the statements of which it is composed.

We define the conjunction elimination operator ce(i) of removing the statement F i from formula F. By the conventional semantics of conjunction, the ce(i) operator is truth-preserving. If you take a formula and remove a statement from it it is still true.

CE:  From  F follows ce(i) F

### Existential quantification

Existential quantifiers and Universal quantifiers have the usual qualities

 Any formula, including the root formula which matches the "document" production of the grammar, may have a set of existential variables indicated by an @forSome declaration. This indicates that, where the formula is considered true, it is true for at least one substitution mapping the existential variables onto non-variables.
As usual, we define a truth-preserving Existential Introduction operator on formulae, that of introducing an existentially quantified variable in place of any term. The operation ei(x, n) is defined as

1.   Creation of a new variable x which occurs nowhere else
2.   The application of σ x/n to F
3.   The addition of x to evF.

 EI: From F  follows ei(x,n) F for any x not occurring anywhere else
### Universal quantification

 Any formula, (including the root formula), may have a set of universal variables. These are indicated by@forAll declarations. The scope of the @forAll is outside the scope of any @forSome.
If both universal and existential quantification are specified for the same context, then the scope of the universal quantification is outside the scope of the existentials:

{ @forAll <#h>. @forSome <#g>. <#g> <#loves> <#h> }.

means

∀<#h> ( ∃<#g>(( <#g><#loves><#h> ))

 The semantics of @forAll is that for any substitution σ = subst(x, n) where x member of uvF, if F is true then σF is also true. Any @forAll declaration may also be removed, preserving truth. Combining these, we define a truth-preserving operation ue(x, n) such that ue(x, n) F is formed by

1.   Removal of x from evF
2.   Application of subst(x, n)

We have the axiom of universal elimination
UE: From  F  follows  ue(x, n)  F  for all x in evF

 As the actual variable used in a formula is quite irrelevant to its semantics, the operation of replacing that variable with another one not used elsewhere within the formula is truth-preserving.

### Variable renaming

We define the operation of variable renaming vr(x,y) on F when x is a member of uvF or is a member of evF.
VR: From  F  follows vr(x, y) F where x is in uvF or evF and y does not occur in F

Occurrence in F is defined recursively in the same way as substitution:x occurs in F iff σ x/n F is not equal to F for arbitrary n.

### Union of formulae

The union H = F∪G of two formulae F and G is formed, as usual, as follows.
A variable renaming operator is applied to G such that the resulting formula G' has no variables which occur un-quantified or differently quantified or existentially quantified in F, and vice-versa.(F and G' may share universal variables).ied or existentially quantified in F, and vice-ver

F∪G is then defined by:

st(F∪G) = stF ∪ st G' ; ev(F∪G) = evF∪ evG' ;  uv(F∪G) = uvF∪ uv G'

### N3 entailment

The operators conjunction elimination, existential elimination, universal introduction and variable renaming are truth preserving.We define an N3 entailment operator (τ) as any operator which is the successive application of any sequence (possibly empty) of such operators.We say a formula F n3-entails a formula τ F.By a combination of SE, EI, UE and VR, τ F logically follows from F.

Note. RDF Graph is a subclass of N3 formula. If F and G are RDF graphs, only CI and EI apply and n3-entailment reduces to simple entailment from RDF Semantics. (@@check for any RDF weirdnesses)We have now defined this simple form of N3-entailment, which amounts to little more than textual inclusion in one expression of a subset of another.We have not defined the normal collection of implication, disjunction and negation which first order logic, as N3logic does provide for first order negation.We have, in the process, defined a substitution operation which we can now use to define implication, which allows us to express rules.

Logic properties and built-in functions
---------------------------------------

We now define the semantics of N3 statements whose predicate is one of a small set of logic properties. These are statements whose truth can be established by performing calculations, or by accessing the web. 
One of our objectives was to make it possible to make statements about, and to query, other statements such as the contents of data in information resources on the web. We have, in formulae, the ability to represent such sets of statements. Now, to allow statements about them, we take some of the relationships we have defined and give them URIs so that these statements and queries can be written in N3.

While the properties we introduced can be used simply as ground facts in a database, is very useful to take advantage of the fact that in fact they can be calculated. In some cases, the truth or falsehood of a binary relation can be calculated; in others, the relationship is a function so one argument (subject or object of the statement) can be calculated from the other.

We now show how such properties are defined, and give examples of how an inference system can use them.A motivation here is to do for logical information what RDF did for data: to provide a common data model and a common syntax, so that extensions of the language are made simply by defining new terms in an ontology.Declarative programing languages like scheme[@@] of course do this. However, they differ in their choice of pairs rather than the RDF binary relational model for data, and lack the use of universal identifiers as symbols.The goal with N3 was to make a minimal extension to the RDF data model, so that the same language could be used for logic and data, which in practice are mixed as a colloidal solution in many real applications.

### Calculated entailment

 We introduce also a set of properties whose truth may be evaluated directly by machine. We call these "built-in" functions.The implementation as built-in functions is not in general required for any implementation of the N3 language, as they can always soundly be treated as ground facts.However, their usefulness derives from their implementation. We say that for example { 1 math:negation-1 } is entailed by calculation.Like other RDF properties, the set is designed to be extensible, as others can use URIs for new functions. A much larger set of such properties is [described for example in the CWM bultt-ins list](https://www.w3.org/2000/10/swap/doc/CwmBuiltins), and the semantics of those are not described here.
When the truth of a statement can be deduced because its predicate is a built-in function, then we call the derivation of the statement from no other evidence calculated entailment.

We now define a small set of such properties which provide the power of N3 logic for inference on the web.

### log:includes

If a formula G n3-entails another formula F, this is expressed in N3 logic as
F log:includes G.

Note. In deference to the fact that RDF treats lists not as terms but as things constructed from first and rest pairs, we can view formulae which include lists as including rdf:first and rdf:rest statements. The effect on inclusion is that two other entailment operations are added: the addition of any statement of the form L rdf:first n where n is the first element of L, or L rdf:rest K where K is list forming the remaining non-first elements of L.  This is not essential to a further understanding of the logic, nor to the operation of a system which does not contain any explicit mention of the terms rdf:first or rdf:rest.

For the discussion of n3-entailment, clearly:

From F  and  F log:includes G  logically follows  G

This can be calculated, because it is a mathematical operation on two compound terms. It is typically used in a query to test the contents of a formula. Below we will show how it can be used in the antecedent of a rule.

### log:notIncludes

 We write of formulae F and G: F log:notIncludes G if it is not the case that G n3-entails F.
As a form of negation, log:notincludes is completely monotonic. It can be evaluated by a mathematical calculation on the value of the two terms: no other knowledge gained can influence the result. This is the scoped negation as failure mentioned in the introduction. This is not a non-monotonic negation as failure.

Note on computation: To ascertain whether G n3-entails F in the worst case involves checking for all possible n3-entailment transformations which are combinations of the variables which occur in G. This operation may be tedious: it is strictly graph isomorphism complete. However the use of symbols rather than variables for a good proportion of nodes makes it much more tractable for practical graphs. The ethos that it is a good idea to give name things with URIs (symbols in N3) is a basic meme of web architecture [AWWW].It has direct practical application in the calculation of n3-entailment, as comparison of graphs whose nodes are labelled is much faster (of order n log (n)))

### log:implies

The log:implies property relates two formulae, expressing implication.  The shorthand notation for log:implies is => .A statement using log:implies, unlike log:includes, cannot be calculated.It is not a built-in function, but the predicate which allows the expression of a rule.
The semantics of implication are standard, but we elaborate them now for completeness.

F log:implies G is true if and only if when the formula F is true then also G is true.

MP:  From F and F => G follows  G

A statement in formula H is of the form F=>G can be considered as rule, in which case, the subject F is the premise (antecedent) of the rule, and the object G is the consequent.

Implication is normally used within a formula with universally quantified variables.For example, universal quantifiers are used with a rule in H as follows.Here H is the formula containing the rules, and K the formula upon which the rules are applied, which we can call the knowledge base.

If F => G is in H, and then for every σ which is a transformation composed of universal eliminations of variables universally quantified in H, then it also follows that σF => σG. Therefore, for every σ such that K includes σF, σG follows from K.

In the particular case that H and K are both the knowledge base, or formula believed true at the top level, then

GMP: From F => G and σF  follows  σG  if σ is a transformation composed of universal eliminations of variables universally quantified at the top level.

#### Filtering

When a knowledge base (formula) contains a lot of information, one way to filter off a subset is to run a set of rules on the knowledge base, and take only the new data which is generated by the rules. This is the filter operation.
When you apply rules to a knowledge base, the filter result of rules in H applied to K is the union of all σG for every statement F => G which is in H, for every σ which s a transformation composed of universal eliminations of variables universally quantified in H such that K includes σF.

#### Repeated application of rules

When rules are added back repeatedly into the same knowledge base, in order to prevent the unnecessary extra growth of the knowledge base, before adding σG to it, there is a check to see whether the H already includes σG, and if it does, the adding of σG is skipped.
Let the result of rules in H applied to K, ρ H K, be the union of K with all σG for every statement F => G which is in H, for every σ which is a transformation composed of universal eliminations of variables universally quantified in H, such that K includes σF, and K does not n3-entail σG.

Note. This form of rule allows existentials in the consequent: it is not datalog.It is is clearly possible in a forward-chaining reasoner to generate an unbounded set of conclusions with rules of the form (using shorthand)

{ ?x a:Person } => { ?x :mother [ a :Person] }.

While this is a trap for the unwary user of a forward-chaining reasoner, it was found to be essential in general to be able to generate arbitrary RDF containing blank nodes, for example when translating information from one ontology into another.

Consider the repeated application of rules in H to K, ρ i H K. If there are no existentially quantified variables in the consequents of any of the rules in H, then this is like datalog, and there will be some threshold n above which no more data is added, and there is a closure: ρ i H K = ρ n H K for all i>n.  In fact in many practical applications even with the datalog constraint removed, there is also a closure. This ρ∞H K is the result of running a forward-chaining reasoner on H and K.

#### Rule Inference on the knowledge base

In the case in which rules are in the same formula as the data, the single rule operation can be written ρ K K, and the closure under rule application ρ∞K K

Cwm note:  the --rules command line option calculates ρ K K, and the --think calculates ρ∞K K. The --filter=H calculates the filter result of H on the knowledge base.
### Examples

Here a simple rule uses log:implies.@prefix log: <http://www.w3.org/2000/10/swap/log#>.

@keywords.

@forAll x, y, z. {x parent y. y sister z} log:implies {x aunt z}

This N3 formula has three universally quantified variables and one statement.The subject of the statement,

{x parent y. y sister z}

is the antecedent of the rule and the object,

{x aunt z}

is the conclusion. Given data

Joe parent Alan.

Alan sister Susie.
a rule engine would conclude

Joe aunt Susie.

As a second example, we use a rule which looks inside a formula:

@forAll x, y, z.

{ x wrote y.

  y log:includes {z weather w}.

  x livesIn z

} log:implies {

  Boston weather y

}.

Here the rule fires when x is bound to a symbol denoting some person who is the author of a formula y, when the formula makes a statement about the weather in (presumably some place) z, and x's home is z.That is, we believe statements about the weather at a place only from people who live there. Given the data

Bob livesIn  Boston.

Bob wrote  { Boston weather sunny }.

Alice livesIn Adelaide.

Alice wrote { Boston weather cold }.

a valid inference would be

Boston weather sunny.

### log:supports

 We say that F log:supports G if there is some sequence of rule inference and/or calculated entailment and/or n3 entailment operators which when applied to F produce G.
### log:conclusion

The log:conclusion property expresses the relationship between a formula and its deductive closure under operations of n3-entailment, rule entailment and calculated entailment.

As noticed above, there are circumstances when this will not be finite.

log:conclusion is the transitive closure of log:supports.

log:supports can be written in terms of log:conclusion and log:includes.

{ ?x log:supports ?y } if and only dan { ?x log:conclusion [ log:includes ?y ]}

However, log:supports may be evaluated in many cases without evaluating log:conclusion: one can determine whether y can be derived from x in many ways, such as backward chaining, without necessarily having to evaluate the (possibly infinite) deductive closure.

Now we have a system which has the capacity to do inference using rules, and to operate on formulae.However, it operates in a vacuum.In fact, our goal is that the system should operate in the context of the web.

Involving the Web
-----------------

We therefore expose the web as a mapping between URIs and the information returned when such a URI is dereferenced, using appropriate protocols.In N3,the information resource is identified by a symbol, which is in fact is its URI. In N3, information is represented in formulae, so we represent the information retrieved as a formula.

 Not all information on the web is, of course in N3. However the architecture we design is that N3 should here be the interlingua. Therefore, from the point of view of this system, the semantics of a document is exactly what can be expressed in N3, no more and no less. 
### log:semantics**

c log:semantics F is true iff c is a document whose logical semantics expressed in N3 is the formula F.

The relation between a document and the logical expression which represents its meaning expressed as N3. The Architecture of the World Wide Web [AWWW] defines algorithms by which a machine can determine representations of document given its symbol (URI).For a representation in N3, this is the formula which corresponds to the document production of the grammar. For a representation in RDF/XML it is the formula which is the entire graph parsed.For any other languages, it may be calculated in as much a specification exists which defines the equivalent N3 semantics for files in that language.

On the meaning of N3 formula

This is not of course the semantics of the document in any absolute sense.It is the semantics expressed in N3.In turn, the full semantics of an N3 formula are grounded, in the definitions of the properties and classes used by the formula.In the HTTP space in which URIs are minted by an authority, definitive information about those definitions may be found by dereferencing the URIs. This information may be in natural language, in some machine-processable logic, or a mixture. Two patterns are important for the semantic web.

One is the grounding of properties and classes by defining them in natural language.Natural language, of course, is not capable of giving an absolute meaning to anything in theory, but in practice a well written document, carefully written by a group of people achieves a precision of definition which is quite sufficient for the community to be able to exchange data using the terms concerned.The other pattern is the raft-like definition of terms in terms of related neighboring ontologies.

@@@@ A full discussion of the grounding of meaning in a web of such definitions is beyond the scope of this article.Here we define only the operation semantics of a system using N3.

@@@@ Edited up to here

The log:semantics of an N3 document is the formula achieved by parsing representation of the document.

 (Cwm note: Cwm knows how to go get a document and parse N3 and RDF/XML , in order to evaluate this. )
Other languages for web documents may be defined whose N3 semantics are therefore also calculable, and so they could be added in due course.

 See for example [GRDDL], [RDF/A], etc

However, for the purpose of the analysis of the language, it is a convenient to consider the semantic web simply as a binary 1:1 relation between a subset of symbols and formulae.

For a document in Notation3, log:semantics is the

 log:parsedAsN3 of the log:contents of the document.

### log:says

log:says is defined by:
F log:says G  iff ∃ H . F log:semantics H and H log:includes G

In other words, loosely a document says something if a representation of it in the sense of the Architecture of the World Wide Web [AWWW] N3-entails it.

The semantics of log:says are similar to that of says in [PCA].

Miscellaneous
-------------

### log:Truth

This is a class of true formulae.

From  { F rdf:type log:Truth } follows F

The cwm engine will process rules in the (indirectly command-line specified) formula or any formula which that declares to be a Truth.

The dereifier will output any described formulae which are described as being in the class Truth.

This class is not at all central to the logic. 
Working with OWL
----------------

@@ Summary

*   owl:sameAs considered the same as N3 value equality for data values.Axioms of equality.log:equalTo and log:notEqualTo compared with owl:SameAs. Compare math and string equality, and SPARQL equality.
*   Operating in equality-aware mode.
*   No attempt at connecting OWL DL language with the N3 logic.
*   Use of functional properties of a datatype conflicting with OWL DL.

Conclusion
----------

The semantics of N3 have been defined, as have some built-in operator properties which add logical inference using rules to the language, and allow rules to define inference which can be drawn from specific web documents on the web, as a function of other information about those documents.

The language has been found to have some useful practical properties.The separation between the Notation3 extensions to RDF and the logic properties has allowed N3 by itself to be used in many other applications directly, and to be used with other properties to provide other functionality such as the expression of patches (updates) [Diff].

The use of log:notIncludes to allow default reasoning without non-monotonic behavior achieves a design goal for distributed rule systems.

* * *

 **[Footnote: Philosophers may be distracted here into worrying about the meaning of meaning. At least we didn't call this function "meaning"! In as much as N3 is used as an interlingua for interoperability for different systems, this for an N3 based system is the meaning expressed by a document.One reviewer was aghast at the definition of semantics as being that of retrieval of a representation, its parsing and assimilation in terms of the local common logical framework. I suspect however that the meaning of the paper to the reviewer could be considered quite equivalently the result of the process of retrieval of a representation of the paper, its parsing by the review, and its assimilation in terms of the reviewer's local logical framework: a similar though perhaps imperfect process.

 Of course, the semantics of many documents are not expressible in logics at all, and many in logic but not in N3. However, we are building a system for which a prime goal is the reading and investigation of machine-readable documents on the web. We use the URI log:semantics for this function and apologize for any heartache it may cause.]
F = G iff |stF| = |stG| and there is some substitution σ such that(∀i .∃j . σ Fi = σG j.)

Appendix: Colophon
------------------

formatting XHTML 1 with nvu

Appendix: Drafting Notes
------------------------

yes, discuss notational abbreviation, but not abstract syntax

hmm... are log:includes, log:implies and such predicates? relations? operators? properties?

To do: describe the syntactic sugar transformations formally to close the loop.