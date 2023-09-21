import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;
import java.util.ArrayList;
import java.util.List;

public class FileUploadApp {
    public static void main(String[] args) {
        JFrame frame = new JFrame("File Upload App");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(600, 400);
        frame.setLayout(new BorderLayout());

        Font headerFont = new Font("Intertight", Font.BOLD, 16);

        JLabel headerLabel = new JLabel("File Upload App - Creado por [Tu Nombre]");
        headerLabel.setFont(headerFont);
        headerLabel.setHorizontalAlignment(SwingConstants.CENTER);
        frame.add(headerLabel, BorderLayout.NORTH);

        JPanel filePanel = new JPanel();
        // Usar BoxLayout con dirección vertical
        filePanel.setLayout(new BoxLayout(filePanel, BoxLayout.Y_AXIS));

        List<FilePanel> filePanelsList = new ArrayList<>();

        // Agregar campo inicial
        addFilePanel(filePanel, filePanelsList);

        JButton addFieldButton = new JButton("Agregar Campo");
        addFieldButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                addFilePanel(filePanel, filePanelsList);
                frame.revalidate();
            }
        });

        frame.add(new JScrollPane(filePanel), BorderLayout.CENTER);

        JPanel buttonPanel = new JPanel();
        buttonPanel.add(addFieldButton);

        frame.add(buttonPanel, BorderLayout.SOUTH);

        frame.setVisible(true);
    }

    private static void addFilePanel(JPanel panel, List<FilePanel> filePanelsList) {
        FilePanel filePanel = new FilePanel();
        panel.add(filePanel);
        filePanelsList.add(filePanel);

        // Agregar espacio vertical de 15 píxeles
        panel.add(Box.createRigidArea(new Dimension(0, 15)));
    }
}

class FilePanel extends JPanel {
    public FilePanel() {
        setLayout(new FlowLayout(FlowLayout.LEFT));

        JLabel label = new JLabel("Archivo:");
        JTextField textField = new JTextField(20);
        JButton browseButton = new JButton("Seleccionar");
        JButton encryptButton = new JButton("Encriptar");
        JButton decryptButton = new JButton("Desencriptar");

        browseButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                JFileChooser fileChooser = new JFileChooser();
                int result = fileChooser.showOpenDialog(FilePanel.this);
                if (result == JFileChooser.APPROVE_OPTION) {
                    File selectedFile = fileChooser.getSelectedFile();
                    textField.setText(selectedFile.getAbsolutePath());
                }
            }
        });

        encryptButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                // Agrega aquí la lógica para encriptar el archivo correspondiente
            }
        });

        decryptButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                // Agrega aquí la lógica para desencriptar el archivo correspondiente
            }
        });

        add(label);
        add(textField);
        add(browseButton);
        add(encryptButton);
        add(decryptButton);
    }
}
