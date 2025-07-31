import React from 'react';
import { FileText, RefreshCw, File, Calendar, Hash } from 'lucide-react';

const DocumentList = ({ documents, onRefresh }) => {
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              Uploaded Documents
            </h2>
            <p className="text-gray-600 mt-1">
              {documents.length} document{documents.length !== 1 ? 's' : ''} uploaded
            </p>
          </div>
          <button
            onClick={onRefresh}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Refresh</span>
          </button>
        </div>

        {/* Documents List */}
        {documents.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No documents uploaded yet
            </h3>
            <p className="text-gray-500 max-w-md mx-auto">
              Upload your first document to start using the AI assistant. 
              Go to the "Upload Documents" tab to get started.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {documents.map((doc, index) => (
              <div
                key={index}
                className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0">
                      <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                        <File className="h-5 w-5 text-primary-600" />
                      </div>
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-medium text-gray-900 truncate">
                        {doc.filename}
                      </h3>
                      
                      <div className="mt-2 flex items-center space-x-6 text-sm text-gray-500">
                        <div className="flex items-center space-x-1">
                          <Hash className="h-4 w-4" />
                          <span>{doc.chunks} chunks</span>
                        </div>
                        
                        <div className="flex items-center space-x-1">
                          <FileText className="h-4 w-4" />
                          <span>{formatFileSize(doc.total_chars)} text</span>
                        </div>
                      </div>
                      
                      <div className="mt-3">
                        <div className="flex items-center space-x-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                              style={{ 
                                width: `${Math.min((doc.chunks / 10) * 100, 100)}%` 
                              }}
                            ></div>
                          </div>
                          <span className="text-xs text-gray-500">
                            {doc.chunks} chunks processed
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex-shrink-0 ml-4">
                    <div className="flex items-center space-x-1 text-xs text-gray-500">
                      <Calendar className="h-3 w-3" />
                      <span>Ready</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Statistics */}
        {documents.length > 0 && (
          <div className="mt-8 bg-gray-50 rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Document Statistics
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-primary-600">
                  {documents.length}
                </div>
                <div className="text-sm text-gray-500">Total Documents</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-primary-600">
                  {documents.reduce((sum, doc) => sum + doc.chunks, 0)}
                </div>
                <div className="text-sm text-gray-500">Total Chunks</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-primary-600">
                  {formatFileSize(documents.reduce((sum, doc) => sum + doc.total_chars, 0))}
                </div>
                <div className="text-sm text-gray-500">Total Text</div>
              </div>
            </div>
          </div>
        )}

        {/* Information */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-blue-900 mb-2">
            How documents are processed:
          </h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Documents are automatically split into smaller chunks for better processing</li>
            <li>• Each chunk is embedded using multilingual sentence transformers</li>
            <li>• Embeddings are stored in FAISS for fast similarity search</li>
            <li>• When you ask questions, the system finds the most relevant chunks</li>
            <li>• The AI assistant uses these chunks to provide accurate answers</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default DocumentList; 