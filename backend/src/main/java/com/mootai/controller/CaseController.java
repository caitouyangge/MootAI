package com.mootai.controller;

import com.mootai.dto.ApiResponse;
import com.mootai.dto.CaseRequest;
import com.mootai.entity.Case;
import com.mootai.service.AiService;
import com.mootai.service.CaseService;
import com.mootai.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.Loader;
import org.apache.pdfbox.text.PDFTextStripper;

@RestController
@RequestMapping("/api/cases")
@RequiredArgsConstructor
@Slf4j
public class CaseController {
    
    private final CaseService caseService;
    private final UserService userService;
    private final AiService aiService;
    
    @Value("${file.upload.dir:uploads}")
    private String uploadDir;
    
    /**
     * 创建案件
     */
    @PostMapping
    public ApiResponse<Case> createCase(@Valid @RequestBody CaseRequest request) {
        try {
            // 从JWT token中获取用户ID（需要实现JWT解析）
            // 暂时使用固定值，后续需要从token中解析
            Long userId = getCurrentUserId();
            Case caseEntity = caseService.createCase(userId, request);
            return ApiResponse.success("案件创建成功", caseEntity);
        } catch (Exception e) {
            return ApiResponse.error(e.getMessage());
        }
    }
    
    /**
     * 获取当前用户的所有案件
     */
    @GetMapping
    public ApiResponse<List<Case>> getUserCases() {
        try {
            Long userId = getCurrentUserId();
            List<Case> cases = caseService.getUserCases(userId);
            return ApiResponse.success("获取成功", cases);
        } catch (Exception e) {
            return ApiResponse.error(e.getMessage());
        }
    }
    
    /**
     * 获取指定案件详情
     */
    @GetMapping("/{id}")
    public ApiResponse<Case> getCase(@PathVariable Long id) {
        try {
            Long userId = getCurrentUserId();
            Case caseEntity = caseService.getCaseById(id, userId);
            if (caseEntity == null) {
                return ApiResponse.error(404, "案件不存在");
            }
            return ApiResponse.success("获取成功", caseEntity);
        } catch (Exception e) {
            return ApiResponse.error(e.getMessage());
        }
    }
    
    /**
     * 上传案件文件
     */
    @PostMapping(value = "/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ApiResponse<List<String>> uploadFiles(@RequestParam("files") MultipartFile[] files) {
        try {
            log.info("收到文件上传请求，文件数量: {}", files != null ? files.length : 0);
            Long userId = getCurrentUserId();
            log.info("当前用户ID: {}", userId);
            List<String> uploadedFileNames = new ArrayList<>();
            
            // 确保上传目录存在
            Path uploadPath = Paths.get(uploadDir, userId.toString());
            Files.createDirectories(uploadPath);
            
            for (MultipartFile file : files) {
                if (file.isEmpty()) {
                    continue;
                }
                
                // 生成唯一文件名（包含原始文件名，便于后续查找）
                String originalFilename = file.getOriginalFilename();
                if (originalFilename == null) {
                    originalFilename = "unnamed";
                }
                
                // 清理文件名中的特殊字符
                String safeFilename = originalFilename.replaceAll("[^a-zA-Z0-9._-]", "_");
                String uniqueFilename = UUID.randomUUID().toString() + "_" + safeFilename;
                
                // 保存文件
                Path filePath = uploadPath.resolve(uniqueFilename);
                Files.copy(file.getInputStream(), filePath, StandardCopyOption.REPLACE_EXISTING);
                
                uploadedFileNames.add(originalFilename);
            }
            
            log.info("文件上传成功，用户ID: {}, 文件数量: {}", userId, uploadedFileNames.size());
            return ApiResponse.success("文件上传成功", uploadedFileNames);
        } catch (IOException e) {
            log.error("文件上传IO异常", e);
            return ApiResponse.error("文件上传失败: " + e.getMessage());
        } catch (RuntimeException e) {
            if (e.getMessage() != null && (e.getMessage().contains("未认证") || e.getMessage().contains("用户不存在"))) {
                log.error("文件上传认证异常", e);
                return ApiResponse.error(401, "未认证: " + e.getMessage());
            }
            log.error("文件上传运行时异常", e);
            return ApiResponse.error("文件上传失败: " + e.getMessage());
        } catch (Exception e) {
            log.error("文件上传异常", e);
            return ApiResponse.error("文件上传失败: " + e.getMessage());
        }
    }
    
    /**
     * 获取上传的文件内容
     */
    @GetMapping("/files/{userId}/{filename}")
    public ResponseEntity<Resource> getFile(@PathVariable Long userId, @PathVariable String filename) {
        try {
            Path filePath = Paths.get(uploadDir, userId.toString(), filename);
            Resource resource = new UrlResource(filePath.toUri());
            
            if (resource.exists() && resource.isReadable()) {
                String contentType = Files.probeContentType(filePath);
                if (contentType == null) {
                    contentType = "application/octet-stream";
                }
                
                return ResponseEntity.ok()
                        .contentType(MediaType.parseMediaType(contentType))
                        .header(HttpHeaders.CONTENT_DISPOSITION, "inline; filename=\"" + resource.getFilename() + "\"")
                        .body(resource);
            } else {
                return ResponseEntity.notFound().build();
            }
        } catch (Exception e) {
            return ResponseEntity.notFound().build();
        }
    }
    
    /**
     * 案件资料自动总结（使用上传的文件）
     */
    @PostMapping("/summarize")
    public ApiResponse<String> summarizeCase(@RequestBody Map<String, Object> request) {
        try {
            @SuppressWarnings("unchecked")
            List<String> fileNames = (List<String>) request.get("fileNames");
            String identity = (String) request.get("identity");
            
            if (fileNames == null || fileNames.isEmpty()) {
                return ApiResponse.error("文件列表不能为空");
            }
            if (identity == null || identity.isEmpty()) {
                return ApiResponse.error("身份不能为空");
            }
            
            // 读取文件内容
            Long userId = getCurrentUserId();
            List<String> fileContents = new ArrayList<>();
            Path uploadPath = Paths.get(uploadDir, userId.toString());
            
            if (Files.exists(uploadPath)) {
                try {
                    // 遍历上传目录中的所有文件
                    Files.list(uploadPath).forEach(path -> {
                        try {
                            String actualFileName = path.getFileName().toString();
                            
                            // 文件名格式：UUID_原始文件名，提取原始文件名部分
                            String originalNameInFile = actualFileName;
                            if (actualFileName.contains("_")) {
                                int firstUnderscore = actualFileName.indexOf("_");
                                originalNameInFile = actualFileName.substring(firstUnderscore + 1);
                            }
                            
                            // 匹配文件名
                            for (String fileName : fileNames) {
                                // 清理文件名进行比较
                                String cleanFileName = fileName.replaceAll("[^a-zA-Z0-9._-]", "_");
                                if (originalNameInFile.equals(cleanFileName) || 
                                    originalNameInFile.endsWith(fileName) ||
                                    fileName.equals(originalNameInFile)) {
                                    // 读取文件内容（根据文件类型）
                                    String content = readFileContent(path, fileName);
                                    if (content != null && !content.isEmpty()) {
                                        fileContents.add("文件名: " + fileName + "\n内容:\n" + content);
                                    } else {
                                        // 如果无法读取内容，至少提供文件名和文件大小信息
                                        try {
                                            long fileSize = Files.size(path);
                                            fileContents.add("文件名: " + fileName + "\n文件大小: " + fileSize + " 字节\n注意: 该文件为二进制文件，无法直接读取文本内容。");
                                        } catch (IOException ex) {
                                            log.warn("获取文件大小失败: " + path, ex);
                                        }
                                    }
                                    break;
                                }
                            }
                        } catch (Exception e) {
                            // 忽略读取失败的文件
                            log.warn("读取文件失败: " + path, e);
                        }
                    });
                } catch (IOException e) {
                    log.warn("遍历上传目录失败", e);
                }
            }
            
            String summary = aiService.summarizeCaseWithContent(fileNames, fileContents, identity);
            return ApiResponse.success("案件总结生成成功", summary);
        } catch (Exception e) {
            return ApiResponse.error("案件总结失败: " + e.getMessage());
        }
    }
    
    /**
     * 读取文件内容（根据文件类型）
     */
    private String readFileContent(Path filePath, String fileName) {
        try {
            // 获取文件扩展名
            String extension = "";
            if (fileName.contains(".")) {
                extension = fileName.substring(fileName.lastIndexOf(".")).toLowerCase();
            }
            
            // 文本文件扩展名列表
            List<String> textExtensions = List.of(
                ".txt", ".md", ".json", ".xml", ".html", ".htm", 
                ".css", ".js", ".java", ".py", ".sql", ".log",
                ".csv", ".properties", ".yaml", ".yml", ".ini",
                ".conf", ".config", ".sh", ".bat", ".ps1"
            );
            
            // 如果是文本文件，尝试读取
            if (textExtensions.contains(extension)) {
                try {
                    return Files.readString(filePath, java.nio.charset.StandardCharsets.UTF_8);
                } catch (java.nio.charset.MalformedInputException e) {
                    // UTF-8读取失败，尝试其他编码
                    try {
                        return Files.readString(filePath, java.nio.charset.StandardCharsets.ISO_8859_1);
                    } catch (Exception ex) {
                        log.warn("无法以UTF-8或ISO-8859-1编码读取文件: " + filePath, ex);
                        return null;
                    }
                }
            } else if (".pdf".equals(extension)) {
                // PDF文件，使用PDFBox提取文本
                return extractTextFromPdf(filePath);
            } else {
                // 其他二进制文件（Word、Excel、图片等）
                log.info("文件 {} 是二进制文件（扩展名: {}），无法直接读取文本内容", fileName, extension);
                return null;
            }
        } catch (Exception e) {
            log.error("读取文件内容异常: " + filePath, e);
            return null;
        }
    }
    
    /**
     * 从PDF文件中提取文本内容
     */
    private String extractTextFromPdf(Path pdfPath) {
        PDDocument document = null;
        try {
            log.info("开始提取PDF文本: {}", pdfPath);
            // PDFBox 3.x 使用 Loader.loadPDF() 替代 PDDocument.load()
            document = Loader.loadPDF(pdfPath.toFile());
            
            PDFTextStripper stripper = new PDFTextStripper();
            stripper.setStartPage(1);
            stripper.setEndPage(document.getNumberOfPages());
            
            String text = stripper.getText(document);
            log.info("PDF文本提取成功，页数: {}, 文本长度: {}", document.getNumberOfPages(), text.length());
            
            return text.trim();
        } catch (Exception e) {
            log.error("提取PDF文本失败: " + pdfPath, e);
            return null;
        } finally {
            if (document != null) {
                try {
                    document.close();
                } catch (IOException e) {
                    log.warn("关闭PDF文档失败", e);
                }
            }
        }
    }
    
    /**
     * 获取当前用户ID
     */
    private Long getCurrentUserId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication != null && authentication.isAuthenticated()) {
            String username = authentication.getName();
            // 通过用户名查找用户ID
            try {
                com.mootai.entity.User user = userService.findByUsername(username);
                return user.getId();
            } catch (Exception e) {
                throw new RuntimeException("用户不存在");
            }
        }
        throw new RuntimeException("未认证");
    }
}

