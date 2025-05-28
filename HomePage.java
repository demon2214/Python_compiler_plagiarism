package net.processmanagmentgui.swing;

import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.util.Random;

public class HomePage extends JFrame {
    private static final long serialVersionUID = 1L;

    // Model
    private static final int TOTAL_FRAMES = 40;
    private ProcessGenerator pcb = new ProcessGenerator();
    private MemoryManager memory = new MemoryManager(TOTAL_FRAMES);
    private Process currentProcess = null;

    // GUI
    private DefaultListModel<String> newQueueModel = new DefaultListModel<>();
    private DefaultListModel<String> readyQueueModel = new DefaultListModel<>();
    private JLabel lblCurrentProc = new JLabel("None");
    private JLabel lblFrames = new JLabel("Frames: " + TOTAL_FRAMES);
    private JLabel lblFree = new JLabel("Free: " + TOTAL_FRAMES);
    private JLabel lblFragment = new JLabel("Fragmentation: 0");
    private JPanel memoryPanel = new JPanel();

    public HomePage() {
        setTitle("Process & Memory Management GUI");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setBounds(250, 100, 1000, 600);
        setResizable(false);

        JPanel root = new JPanel(new BorderLayout(8, 8));
        setContentPane(root);

        // Top status
        JPanel top = new JPanel(new FlowLayout(FlowLayout.LEFT, 20, 10));
        top.setBackground(new Color(133, 203, 217));
        top.add(lblFrames);
        top.add(lblFree);
        top.add(lblFragment);
        root.add(top, BorderLayout.NORTH);

        // Center panels
        JPanel center = new JPanel(new GridLayout(1, 4, 8, 8));
        root.add(center, BorderLayout.CENTER);

        // New Queue
        JList<String> newQueueList = new JList<>(newQueueModel);
        center.add(wrapPanel("New Process Queue", new JScrollPane(newQueueList)));

        // Ready Queue
        JList<String> readyQueueList = new JList<>(readyQueueModel);
        center.add(wrapPanel("Ready Queue", new JScrollPane(readyQueueList)));

        // Current Process
        JPanel current = new JPanel(new BorderLayout());
        current.setBackground(new Color(255, 200, 109));
        JLabel lbl1 = new JLabel("Current Process", SwingConstants.CENTER);
        lbl1.setFont(new Font("Times New Roman", Font.BOLD, 18));
        current.add(lbl1, BorderLayout.NORTH);
        lblCurrentProc.setFont(new Font("Monospaced", Font.BOLD, 24));
        lblCurrentProc.setHorizontalAlignment(SwingConstants.CENTER);
        current.add(lblCurrentProc, BorderLayout.CENTER);
        center.add(current);

        // Memory
        memoryPanel.setLayout(new GridLayout(10, 4, 2,2));
        updateMemoryPanel();
        center.add(wrapPanel("Memory", memoryPanel));

        // Controller
        JPanel controls = new JPanel(new GridLayout(6, 1, 8, 8));
        controls.setBackground(new Color(133, 203, 217));
        JButton btnAdd = new JButton("Add Process");
        JButton btnLTS = new JButton("L-T Scheduler");
        JButton btnSTS = new JButton("S-T Scheduler");
        JButton btnStop = new JButton("Stop");
        JButton btnFrag = new JButton("Show Fragmentation");
        JButton btnDefrag = new JButton("Defragmentation");
        controls.add(btnAdd);
        controls.add(btnLTS);
        controls.add(btnSTS);
        controls.add(btnStop);
        controls.add(btnFrag);
        controls.add(btnDefrag);
        root.add(controls, BorderLayout.EAST);

        // Actions

        // Add Process
        btnAdd.addActionListener(e -> {
            int mem = new Random().nextInt(6) + 2; // Random need 2-7 frames
            int start = memory.allocate(mem);
            if (start == -1) {
                JOptionPane.showMessageDialog(this, "Not enough memory for new process!", "Error", JOptionPane.ERROR_MESSAGE);
                return;
            }
            Process p = new Process(mem);
            p.setMemStart(start);
            pcb.addProcess(p);
            updateQueues();
            updateMemoryPanel();
        });

        // LT Scheduler
        btnLTS.addActionListener(e -> {
            Process p = pcb.moveToReady();
            if (p == null) {
                JOptionPane.showMessageDialog(this, "No process in New Queue!", "Info", JOptionPane.INFORMATION_MESSAGE);
            }
            updateQueues();
        });

        // ST Scheduler
        btnSTS.addActionListener(e -> {
            Process p = pcb.runProcess();
            if (p == null) {
                JOptionPane.showMessageDialog(this, "No process in Ready Queue!", "Info", JOptionPane.INFORMATION_MESSAGE);
                return;
            }
            currentProcess = p;
            lblCurrentProc.setText("P" + p.getPid() + " (" + p.getMemoryRequired() + " frames)");
            updateQueues();
        });

        // Stop
        btnStop.addActionListener(e -> {
            pcb.clear();
            memory.reset();
            currentProcess = null;
            lblCurrentProc.setText("None");
            updateQueues();
            updateMemoryPanel();
        });

        // Show Fragmentation
        btnFrag.addActionListener(e -> {
    String details = memory.getFragmentationDetails();
    JOptionPane.showMessageDialog(this, details, "Fragmentation Details", JOptionPane.INFORMATION_MESSAGE);
});

        // Defragmentation
        btnDefrag.addActionListener(e -> {
            memory.defragment();
            updateMemoryPanel();
            JOptionPane.showMessageDialog(this, "Memory defragmented!", "Defragmentation", JOptionPane.INFORMATION_MESSAGE);
        });

        // Right-click on current process: Terminate (reclaim memory)
        lblCurrentProc.addMouseListener(new MouseAdapter() {
            public void mouseClicked(MouseEvent e) {
                if (SwingUtilities.isRightMouseButton(e) && currentProcess != null) {
                    memory.free(currentProcess.getMemStart(), currentProcess.getMemoryRequired());
                    JOptionPane.showMessageDialog(HomePage.this, "Process P" + currentProcess.getPid() + " terminated and memory freed.");
                    currentProcess = null;
                    lblCurrentProc.setText("None");
                    updateMemoryPanel();
                }
            }
        });

        updateQueues();
    }

    private JPanel wrapPanel(String title, JComponent comp) {
        JPanel p = new JPanel(new BorderLayout());
        JLabel l = new JLabel(title, SwingConstants.CENTER);
        l.setFont(new Font("Times New Roman", Font.BOLD, 17));
        p.add(l, BorderLayout.NORTH);
        p.add(comp, BorderLayout.CENTER);
        p.setBorder(BorderFactory.createLineBorder(new Color(255, 200, 109), 2));
        p.setBackground(new Color(133, 203, 217));
        return p;
    }

    private void updateQueues() {
        newQueueModel.clear();
        for (Process p : pcb.getNewQueue().getAll()) newQueueModel.addElement(p.toString());
        readyQueueModel.clear();
        for (Process p : pcb.getReadyQueue().getAll()) readyQueueModel.addElement(p.toString());
        lblFree.setText("Free: " + memory.getFreeFrames());
        lblFragment.setText("Fragmentation: " + memory.getFragmentationDetails());
    }

    private void updateMemoryPanel() {
        memoryPanel.removeAll();
        boolean[] used = memory.getFrames();
        for (int i = 0; i < used.length; i++) {
            JPanel b = new JPanel();
            b.setBackground(used[i] ? Color.RED : Color.GREEN);
            b.setBorder(BorderFactory.createLineBorder(Color.BLACK, 1));
            memoryPanel.add(b);
        }
        memoryPanel.revalidate();
        memoryPanel.repaint();
        lblFree.setText("Free: " + memory.getFreeFrames());
        lblFragment.setText("Fragmentation: " + memory.getFragmentationDetails());
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new HomePage().setVisible(true));
    }
}