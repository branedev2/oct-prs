import recur.*;

import java.util.List;
import java.util.ArrayList;
import java.util.Arrays;
import java.io.Writer;
import java.io.BufferedWriter;
import java.io.OutputStreamWriter;
import java.io.FileOutputStream;
import java.io.File;
import java.util.Scanner;
import java.io.FileReader;


public class APL {

  private static int decomposeCount = 0;
  private static final Object lock = new Object();
  private static final int GIVEUP = 8;

  public static <T> double[] compute(Graph<T> graph, T u, T v, int presuffix, int trials) {
    String rep = graph.translateOriginal();
    // System.out.println("Graph: " + graph);
    try (Writer writer = new BufferedWriter(new OutputStreamWriter(
              new FileOutputStream("original.txt"), "utf-8"))) {
      writer.write(rep);
    } catch (Exception e) {
      System.out.println("Not found!");
    }
    Node<T> start = graph.getNode(u);
    Node<T> end = graph.getNode(v);
    
    if (start == null || end == null) {
      throw new IllegalArgumentException();
    }
    return compute(graph, start, end, presuffix, trials);
  }

  public static <T> double[] compute(Graph<T> graph, Node<T> u, Node<T> v, int presuffix, int trials) {
    double[] result = computeHelper(graph, u, v, presuffix, trials);
    result[1] = result[1] / result[0];
    return result;
  }

  public static <T> double[] computeHelper(Graph<T> graph, Node<T> u, Node<T> v, int presuffix, int trials) {
    TarjanSCC<T> tarjan = new TarjanSCC<>(graph);
    // System.out.println("Tarjan's Algorithm: " + tarjan);
    List<SCC<T>> sccs = tarjan.getSCCs();

    if (sccs.size() == graph.size()) {
      return PathFinder.superDagTraversal(graph, u, v);
    } else {
      Graph<T> supergraph = new Graph<>();
      List<Node<T>> nodes = populateGraph(supergraph, sccs, u, v);
      u = nodes.get(0);
      v = nodes.get(1);
      // System.out.println("SuperGraph: \n" + supergraph);
      decomposeGraph(supergraph, sccs, u, v, presuffix, trials);
      return PathFinder.superDagTraversal(supergraph, u, v);
    }
  }

  private static <T> boolean isDag(Graph<T> graph) {
    TarjanSCC<T> tarjan = new TarjanSCC<>(graph);
    List<SCC<T>> sccs = tarjan.getSCCs();
    return sccs.size() == graph.size();
  }

  private static <T> void decomposeGraph(Graph<T> graph, List<SCC<T>> sccs, Node<T> u, Node<T> v, int presuffix, int trials) {
    for (SCC<T> scc : sccs) {
      for (Node<T> entryNode : scc.getEntryNodes()) {
        for (Node<T> exitNode : scc.getExitNodes()) {
          if (!entryNode.equalValue(exitNode)) {
            // System.out.println("X Node: " + entryNode);
            // System.out.println("Y Node: " + exitNode);
            Graph<T> subgraph = new Graph<>();
            List<Node<T>> nodes = makeSubgraph(subgraph, scc, entryNode, exitNode);
            double[] result = new double[2];
            decomposeCount++;
            boolean isDag = isDag(subgraph);

            if (decomposeCount % GIVEUP == 0 && !isDag) {
              String rep = subgraph.translateToString(entryNode.getValue(), exitNode.getValue(), trials);
              try {
                File file = new File("subgraph.txt");
                if (file.exists()) {
                  file.delete();
                }
              } catch (Exception e) {
                System.out.println("Subgraph txt Deletion Error");
              }
              try (Writer writer = new BufferedWriter(new OutputStreamWriter(
                        new FileOutputStream("subgraph.txt"), "utf-8"))) {
                writer.write(rep);
              } catch (Exception e) {
                System.out.println("Writing Subgraph Problem");
              }

              Integer uVal = (Integer) entryNode.getValue();
              Integer vVal = (Integer) exitNode.getValue();
              PairAndSetGenerator.startGeneration(presuffix, uVal, vVal);

              try {
                File file = new File("results.txt");
                while (!file.exists()) {
// {fact rule=path-traversal@v1.0 defects=1}
                  synchronized(lock) {
                    System.out.println("waiting");
                    lock.wait(1000);
                  }
                }
// defect
                Scanner in = new Scanner(new FileReader(file.getName()));
                if (in.hasNext()) {
                  result[0] = in.nextDouble();
                  result[1] = in.nextDouble();
                  // System.out.println(result[0] + " " + result[1]);
                }
// {/fact}
                file.delete();
              } catch (Exception e) {
                System.out.println("Not found!");
              }
              
            }

            if (result[0] != 0.0d) {
              if (decomposeCount % GIVEUP != 0) {
                System.out.println("Erroniously using Tobi's Algorithm");
              }
              graph.addSuperEdge(entryNode, exitNode, result[0], (result[1]*result[0]));
            } else {
              if (decomposeCount % GIVEUP == 0 && !isDag) {
                System.out.println("Erroniously using Daniel's Algorithm");
              }
              double[] values = APL.computeHelper(subgraph, nodes.get(0), nodes.get(1), presuffix, trials);
              graph.addSuperEdge(entryNode, exitNode, values[0], values[1]);
            }
          }
        }
      }
    }
  }

  // subgraph = copy of SCC with (*, x), (y, *), crossEdges, and nodes with no edges removed
  // does not include split node of y. Fakes that you are trying to get from x to y.splitNode
  private static <T> List<Node<T>> makeSubgraph(Graph<T> subgraph, SCC<T> scc, Node<T> x, Node<T> y) {
    Node<T> originalY = y;
    y = y.getSplitNode() != null ? y.getSplitNode() : y;
    for (Node<T> node : scc.getNodes()) {
      if (!node.equals(y)) {
        for (Node<T> adjNode : node.getAdjacents()) {
          if (scc.contains(adjNode) && !adjNode.equals(x)) {
            if (!node.equalValue(adjNode)) {
              subgraph.addEdge(node, adjNode); // adding edge will also create the nodes
            } 
          }
        }
      }
    }

    // System.out.println("Subgraph:\n" + subgraph);
    Node<T> start = subgraph.findNode(x);
    Node<T> end = subgraph.findNode(y);
    if (start == null || end == null) {
      throw new IllegalArgumentException();
    }
    return new ArrayList<>(Arrays.asList(start, end));
  }

  private static <T> List<Node<T>> populateGraph(Graph<T> graph, List<SCC<T>> sccs, Node<T> u, Node<T> v) {
    List<Node<T>> nodes = addSpecialNodes(graph, sccs, u, v);
    addCrossEdges(graph, sccs);
    addSelfEdges(graph, sccs);
    return nodes;
  }

  private static <T> List<Node<T>> addSpecialNodes(Graph<T> graph, List<SCC<T>> sccs, Node<T> u, Node<T> v) {
    for (SCC<T> scc : sccs) {
      // Flagging the nodes to be considered as entry or exit
      if (scc.contains(u)) {
        u.setEntry(true);
      }
      if (scc.contains(v)) {
        v.setExit(true);
      }

      int i = 0;
      for (Node<T> entryNode : scc.getEntryNodes()) {
        Node<T> n = graph.addNode(entryNode);
      }
      int j = 0;
      for (Node<T> exitNode : scc.getExitNodes()) {
        Node<T> n = graph.addNode(exitNode);
      }
    }
    Node<T> entryU = graph.findEntryNode(u.getValue());
    Node<T> exitV = graph.findExitNode(v.getValue());
    return new ArrayList<>(Arrays.asList(entryU, exitV));
  }

  private static <T> void addCrossEdges(Graph<T> graph, List<SCC<T>> sccs) {
    for (SCC<T> scc : sccs) {
      for (Node<T> exitNode : scc.getExitNodes()) {
        for (Node<T> adjNode : exitNode.getAdjacents()) {
          if (!scc.contains(adjNode)) {
            graph.addEdge(exitNode, adjNode);
          }
        }
      }
    }
  }

  private static <T> void addSelfEdges(Graph<T> graph, List<SCC<T>> sccs) {
    for (SCC<T> scc : sccs) {
      for (Node<T> entryNode : scc.getEntryNodes()) {
        Node<T> splitNode = entryNode.getSplitNode();
        if (splitNode != null) {
          graph.addSuperEdge(entryNode, splitNode, 1.0, 0.0);
        }
      }
    }
  }

}
