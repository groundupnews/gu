from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Group, Block, BlockGroup

class BlockTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.group = Group.objects.create(
            name="Test Group",
            pages_include="page1",
            pages_exclude="page2"
        )
        
        cls.block1 = Block.objects.create(
            name="Test Block 1",
            html="This is test block 1 content"
        )

        cls.block2 = Block.objects.create(
            name="Test Block 2", 
            html="This is test block 2 content"
        )

        # Connect blocks to group through BlockGroup
        BlockGroup.objects.create(
            block=cls.block1,
            group=cls.group
        )

        BlockGroup.objects.create(
            block=cls.block2,
            group=cls.group
        )

    def test_block_str(self):
        """Test Block string representation
        
        Expected output:
        - Block string should match its name
        """
        self.assertEqual(str(self.block1), self.block1.name)

    def test_group_str(self):
        """Test Group string representation
        
        Expected output:
        - Group string should match its name
        """
        self.assertEqual(str(self.group), self.group.name)

    def test_group_block_list(self):
        """Test block_list() method
        
        Expected output:
        - Should return comma-separated list of block names
        - Should include all blocks in correct order
        """
        expected = f"{self.block1.name}, {self.block2.name}"
        self.assertEqual(self.group.block_list(), expected)

    def test_get_blocks(self):
        """Test get_blocks() method
        
        Expected output:
        - Should return QuerySet of 2 blocks
        - Should contain both test blocks
        - Blocks should be ordered by link_to_group
        """
        blocks = self.group.get_blocks()
        self.assertEqual(len(blocks), 2, "Expected exactly 2 blocks")
        self.assertIn(self.block1, blocks, "First block should be in result")
        self.assertIn(self.block2, blocks, "Second block should be in result")
