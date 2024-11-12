#include "packet_handler.h"

#include "util/memory.h"

void handlePackets() {
    HTTP_PACKET *rcvPacketHTTP = RCV_PACKET_BUFF_ADDRESS;
    PACKET *rcvPacket = &rcvPacketHTTP->packet;

    u32 result;
    while (TRUE) {
        result = downloadPacket(rcvPacketHTTP);
        switch (result) {
            case 1:
                if (!handlePacket(rcvPacket) || !rcvPacket->header.requestNext)
                    return;
            default:
                break;
        }
    }
}

static inline u32 downloadPacket(HTTP_PACKET *packet) {
    fetchPacket(packet);
    return handleAsync();
}

static inline u32 uploadPacket(PACKET *packet) {
    sendPacket(packet);
    return handleAsync();
}

static inline u32 handleAsync() {
    while (TRUE) {
        tryAsyncUpdate();
        if (isAsyncComplete())
            break;
    }
    return getAsyncResult();
}

BOOL handlePacket(PACKET *packet) {
    switch (packet->header.packetType){
        case TYPE_NONE:
            return FALSE;
        case TYPE_DATA_PACKET:
            return handleDataPacket((DATA_PACKET*)packet);
        case TYPE_CODE_PACKET:
            return handleCodePacket((CODE_PACKET*)packet);
        case TYPE_DUMP_PACKET:
            return handleDumpPacket((DUMP_PACKET*)packet);
        default:
            return FALSE;
    }
}

BOOL handleDataPacket(DATA_PACKET *packet) {
    if (packet->header.destinationAddress == NULL)
        return FALSE;

    memcp(packet->header.destinationAddress, packet->data, packet->header.size);
    return TRUE;
}

BOOL handleCodePacket(CODE_PACKET *packet) {
    return fp_thumb(packet->data, BOOL, ())();
}

BOOL handleDumpPacket(DUMP_PACKET *packet) {
    if (packet->header.dump_address == NULL)
        return FALSE;

    uploadPacket(packet->header.dump_address);
    return TRUE;
}

BOOL setPacketSizes() {
    // upload
    // *(u16*)0x0222dbcc = 0x4a0f;
    // *(u16*)0x0222dbe0 = 0x4b1f;
    // *(u16*)0x0222dbe2 = 0x4a0a;

    // *(u32*)0x0222dc0c = CUSTOM_PACKET_SIZE;

    // download
    *(u16*)0x0222dcc8 = 0x480d; // this was noted as 0x4A but I think it should be reg 0 not 2
    *(u16*)0x0222dcce = 0x491c;

    *(u32*)0x0222dd00 = CUSTOM_PACKET_SIZE;
    return TRUE;
}
